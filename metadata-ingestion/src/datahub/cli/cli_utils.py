import json
import logging
import os
import os.path
import sys
import typing
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

import click
import requests
from deprecated import deprecated
from requests.models import Response
from requests.sessions import Session

from datahub.cli import config_utils
from datahub.emitter.aspect import ASPECT_MAP, TIMESERIES_ASPECT_MAP
from datahub.emitter.request_helper import make_curl_command
from datahub.emitter.serialization_helper import post_json_transform
from datahub.metadata.schema_classes import _Aspect
from datahub.utilities.urns.urn import Urn, guess_entity_type

log = logging.getLogger(__name__)

ENV_METADATA_HOST_URL = "DATAHUB_GMS_URL"
ENV_METADATA_HOST = "DATAHUB_GMS_HOST"
ENV_METADATA_PORT = "DATAHUB_GMS_PORT"
ENV_METADATA_PROTOCOL = "DATAHUB_GMS_PROTOCOL"
ENV_METADATA_TOKEN = "DATAHUB_GMS_TOKEN"
ENV_DATAHUB_SYSTEM_CLIENT_ID = "DATAHUB_SYSTEM_CLIENT_ID"
ENV_DATAHUB_SYSTEM_CLIENT_SECRET = "DATAHUB_SYSTEM_CLIENT_SECRET"

config_override: Dict = {}

# TODO: Many of the methods in this file duplicate logic that already lives
# in the DataHubGraph client. We should refactor this to use the client instead.
# For the methods that aren't duplicates, that logic should be moved to the client.


def set_env_variables_override_config(url: str, token: Optional[str]) -> None:
    """Should be used to override the config when using rest emitter"""
    config_override[ENV_METADATA_HOST_URL] = url
    if token is not None:
        config_override[ENV_METADATA_TOKEN] = token


def get_details_from_env() -> Tuple[Optional[str], Optional[str]]:
    host = os.environ.get(ENV_METADATA_HOST)
    port = os.environ.get(ENV_METADATA_PORT)
    token = os.environ.get(ENV_METADATA_TOKEN)
    protocol = os.environ.get(ENV_METADATA_PROTOCOL, "http")
    url = os.environ.get(ENV_METADATA_HOST_URL)
    if port is not None:
        url = f"{protocol}://{host}:{port}"
        return url, token
    # The reason for using host as URL is backward compatibility
    # If port is not being used we assume someone is using host env var as URL
    if url is None and host is not None:
        log.warning(
            f"Do not use {ENV_METADATA_HOST} as URL. Use {ENV_METADATA_HOST_URL} instead"
        )
    return url or host, token


def first_non_null(ls: List[Optional[str]]) -> Optional[str]:
    return next((el for el in ls if el is not None and el.strip() != ""), None)


def get_system_auth() -> Optional[str]:
    system_client_id = os.environ.get(ENV_DATAHUB_SYSTEM_CLIENT_ID)
    system_client_secret = os.environ.get(ENV_DATAHUB_SYSTEM_CLIENT_SECRET)
    if system_client_id is not None and system_client_secret is not None:
        return f"Basic {system_client_id}:{system_client_secret}"
    return None


def parse_run_restli_response(response: requests.Response) -> dict:
    response_json = response.json()
    if response.status_code != 200:
        if isinstance(response_json, dict):
            if "message" in response_json:
                click.secho("Failed to execute operation", fg="red")
                click.secho(f"{response_json['message']}", fg="red")
            else:
                click.secho(f"Failed with \n{response_json}", fg="red")
        else:
            response.raise_for_status()
        exit()

    if not isinstance(response_json, dict):
        click.echo(
            f"Received error, please check your {config_utils.CONDENSED_DATAHUB_CONFIG_PATH}"
        )
        click.echo()
        click.echo(response_json)
        exit()

    summary = response_json.get("value")
    if not isinstance(summary, dict):
        click.echo(
            f"Received error, please check your {config_utils.CONDENSED_DATAHUB_CONFIG_PATH}"
        )
        click.echo()
        click.echo(response_json)
        exit()

    return summary


def format_aspect_summaries(summaries: list) -> typing.List[typing.List[str]]:
    local_timezone = datetime.now().astimezone().tzinfo
    return [
        [
            row.get("urn"),
            row.get("aspectName"),
            datetime.fromtimestamp(row.get("timestamp") / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            + f" ({local_timezone})",
        ]
        for row in summaries
    ]


def post_rollback_endpoint(
    session: Session,
    gms_host: str,
    payload_obj: dict,
    path: str,
) -> typing.Tuple[typing.List[typing.List[str]], int, int, int, int, typing.List[dict]]:
    url = gms_host + path

    payload = json.dumps(payload_obj)
    response = session.post(url, payload)

    summary = parse_run_restli_response(response)
    rows = summary.get("aspectRowSummaries", [])
    entities_affected = summary.get("entitiesAffected", 0)
    aspects_reverted = summary.get("aspectsReverted", 0)
    aspects_affected = summary.get("aspectsAffected", 0)
    unsafe_entity_count = summary.get("unsafeEntitiesCount", 0)
    unsafe_entities = summary.get("unsafeEntities", [])
    rolled_back_aspects = list(
        filter(lambda row: row["runId"] == payload_obj["runId"], rows)
    )

    if len(rows) == 0:
        click.secho(f"No entities found. Payload used: {payload}", fg="yellow")

    structured_rolled_back_results = format_aspect_summaries(rolled_back_aspects)
    return (
        structured_rolled_back_results,
        entities_affected,
        aspects_reverted,
        aspects_affected,
        unsafe_entity_count,
        unsafe_entities,
    )


def get_entity(
    session: Session,
    gms_host: str,
    urn: str,
    aspect: Optional[List] = None,
    cached_session_host: Optional[Tuple[Session, str]] = None,
) -> Dict:
    if urn.startswith("urn%3A"):
        # we assume the urn is already encoded
        encoded_urn: str = urn
    elif urn.startswith("urn:"):
        encoded_urn = Urn.url_encode(urn)
    else:
        raise Exception(
            f"urn {urn} does not seem to be a valid raw (starts with urn:) or encoded urn (starts with urn%3A)"
        )

    # TODO: Replace with DataHubGraph.get_entity_raw.
    endpoint: str = f"/entitiesV2/{encoded_urn}"

    if aspect and len(aspect):
        endpoint = f"{endpoint}?aspects=List(" + ",".join(aspect) + ")"

    response = session.get(gms_host + endpoint)
    response.raise_for_status()
    return response.json()


def post_entity(
    session: Session,
    gms_host: str,
    urn: str,
    entity_type: str,
    aspect_name: str,
    aspect_value: Dict,
    cached_session_host: Optional[Tuple[Session, str]] = None,
    is_async: Optional[str] = "false",
) -> int:
    endpoint: str = "/aspects/?action=ingestProposal"

    proposal = {
        "proposal": {
            "entityType": entity_type,
            "entityUrn": urn,
            "aspectName": aspect_name,
            "changeType": "UPSERT",
            "aspect": {
                "contentType": "application/json",
                "value": json.dumps(aspect_value),
            },
        },
        "async": is_async,
    }
    payload = json.dumps(proposal)
    url = gms_host + endpoint
    curl_command = make_curl_command(session, "POST", url, payload)
    log.debug(
        "Attempting to emit to DataHub GMS; using curl equivalent to:\n%s",
        curl_command,
    )
    response = session.post(url, payload)
    if not response.ok:
        try:
            log.info(response.json()["message"].strip())
        except Exception:
            log.info(f"post_entity failed: {response.text}")
    response.raise_for_status()
    return response.status_code


def _get_pydantic_class_from_aspect_name(aspect_name: str) -> Optional[Type[_Aspect]]:
    return ASPECT_MAP.get(aspect_name)


def get_latest_timeseries_aspect_values(
    session: Session,
    gms_host: str,
    entity_urn: str,
    timeseries_aspect_name: str,
    cached_session_host: Optional[Tuple[Session, str]],
) -> Dict:
    query_body = {
        "urn": entity_urn,
        "entity": guess_entity_type(entity_urn),
        "aspect": timeseries_aspect_name,
        "latestValue": True,
    }
    end_point = "/aspects?action=getTimeseriesAspectValues"
    try:
        response = session.post(url=gms_host + end_point, data=json.dumps(query_body))
        response.raise_for_status()
        return response.json()
    except Exception:
        # Ignore exceptions
        return {}


def get_aspects_for_entity(
    session: Session,
    gms_host: str,
    entity_urn: str,
    aspects: List[str],
    typed: bool = False,
    cached_session_host: Optional[Tuple[Session, str]] = None,
) -> Dict[str, Union[dict, _Aspect]]:
    # Process non-timeseries aspects
    non_timeseries_aspects = [a for a in aspects if a not in TIMESERIES_ASPECT_MAP]
    entity_response = get_entity(
        session, gms_host, entity_urn, non_timeseries_aspects, cached_session_host
    )
    aspect_list: Dict[str, dict] = entity_response["aspects"]

    # Process timeseries aspects & append to aspect_list
    timeseries_aspects: List[str] = [a for a in aspects if a in TIMESERIES_ASPECT_MAP]
    for timeseries_aspect in timeseries_aspects:
        timeseries_response: Dict = get_latest_timeseries_aspect_values(
            session, gms_host, entity_urn, timeseries_aspect, cached_session_host
        )
        values: List[Dict] = timeseries_response.get("value", {}).get("values", [])
        if values:
            aspect_cls: Optional[Type] = _get_pydantic_class_from_aspect_name(
                timeseries_aspect
            )
            if aspect_cls is not None:
                ts_aspect = values[0]["aspect"]
                # Decode the json-encoded generic aspect value.
                ts_aspect["value"] = json.loads(ts_aspect["value"])
                aspect_list[timeseries_aspect] = ts_aspect

    aspect_map: Dict[str, Union[dict, _Aspect]] = {}
    for aspect_name, a in aspect_list.items():
        aspect_py_class: Optional[Type[Any]] = _get_pydantic_class_from_aspect_name(
            aspect_name
        )

        aspect_dict = a["value"]
        if not typed:
            aspect_map[aspect_name] = aspect_dict
        elif aspect_py_class:
            try:
                post_json_obj = post_json_transform(aspect_dict)
                aspect_map[aspect_name] = aspect_py_class.from_obj(post_json_obj)
            except Exception as e:
                log.error(f"Error on {json.dumps(aspect_dict)}", e)
        else:
            log.debug(f"Failed to find class for aspect {aspect_name}")

    if aspects:
        return {k: v for (k, v) in aspect_map.items() if k in aspects}
    else:
        return dict(aspect_map)


def make_shim_command(name: str, suggestion: str) -> click.Command:
    @click.command(
        name=name,
        context_settings=dict(
            ignore_unknown_options=True,
            allow_extra_args=True,
        ),
    )
    @click.pass_context
    def command(ctx: click.Context) -> None:
        """<disabled due to missing dependencies>"""

        click.secho(
            "This command is disabled due to missing dependencies. "
            f"Please {suggestion} to enable it.",
            fg="red",
        )
        ctx.exit(1)

    return command


def get_session_login_as(
    username: str, password: str, frontend_url: str
) -> requests.Session:
    session = requests.Session()
    headers = {
        "Content-Type": "application/json",
    }
    system_auth = get_system_auth()
    if system_auth is not None:
        session.headers.update({"Authorization": system_auth})
    else:
        data = '{"username":"' + username + '", "password":"' + password + '"}'
        response = session.post(f"{frontend_url}/logIn", headers=headers, data=data)
        response.raise_for_status()
    return session


def _ensure_valid_gms_url_acryl_cloud(url: str) -> str:
    if "acryl.io" not in url:
        return url
    if url.startswith("http://"):
        url = url.replace("http://", "https://")
    if url.endswith("acryl.io"):
        url = f"{url}/gms"
    return url


def fixup_gms_url(url: str) -> str:
    if url is None:
        return ""
    if url.endswith("/"):
        url = url.rstrip("/")
    url = _ensure_valid_gms_url_acryl_cloud(url)
    return url


def guess_frontend_url_from_gms_url(gms_url: str) -> str:
    gms_url = fixup_gms_url(gms_url)
    url = gms_url
    if url.endswith("/gms"):
        url = gms_url.rstrip("/gms")
    if url.endswith("8080"):
        url = url[:-4] + "9002"
    return url


def generate_access_token(
    username: str,
    password: str,
    gms_url: str,
    token_name: Optional[str] = None,
    validity: str = "ONE_HOUR",
) -> Tuple[str, str]:
    frontend_url = guess_frontend_url_from_gms_url(gms_url)
    session = get_session_login_as(
        username=username,
        password=password,
        frontend_url=frontend_url,
    )
    now = datetime.now()
    timestamp = now.astimezone().isoformat()
    if token_name is None:
        token_name = f"cli token {timestamp}"
    json = {
        "query": """mutation createAccessToken($input: CreateAccessTokenInput!) {
            createAccessToken(input: $input) {
              accessToken
              metadata {
                id
                actorUrn
                ownerUrn
                name
                description
              }
            }
        }""",
        "variables": {
            "input": {
                "type": "PERSONAL",
                "actorUrn": f"urn:li:corpuser:{username}",
                "duration": validity,
                "name": token_name,
            }
        },
    }
    response = session.post(f"{frontend_url}/api/v2/graphql", json=json)
    response.raise_for_status()
    return token_name, response.json().get("data", {}).get("createAccessToken", {}).get(
        "accessToken", None
    )
