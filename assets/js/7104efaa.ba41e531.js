"use strict";(self.webpackChunkdocs_website=self.webpackChunkdocs_website||[]).push([[5385],{3905:(e,t,a)=>{a.d(t,{Zo:()=>u,kt:()=>m});var n=a(67294);function r(e,t,a){return t in e?Object.defineProperty(e,t,{value:a,enumerable:!0,configurable:!0,writable:!0}):e[t]=a,e}function i(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),a.push.apply(a,n)}return a}function o(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?i(Object(a),!0).forEach((function(t){r(e,t,a[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):i(Object(a)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))}))}return e}function l(e,t){if(null==e)return{};var a,n,r=function(e,t){if(null==e)return{};var a,n,r={},i=Object.keys(e);for(n=0;n<i.length;n++)a=i[n],t.indexOf(a)>=0||(r[a]=e[a]);return r}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(n=0;n<i.length;n++)a=i[n],t.indexOf(a)>=0||Object.prototype.propertyIsEnumerable.call(e,a)&&(r[a]=e[a])}return r}var s=n.createContext({}),c=function(e){var t=n.useContext(s),a=t;return e&&(a="function"==typeof e?e(t):o(o({},t),e)),a},u=function(e){var t=c(e.components);return n.createElement(s.Provider,{value:t},e.children)},d={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},p=n.forwardRef((function(e,t){var a=e.components,r=e.mdxType,i=e.originalType,s=e.parentName,u=l(e,["components","mdxType","originalType","parentName"]),p=c(a),m=r,f=p["".concat(s,".").concat(m)]||p[m]||d[m]||i;return a?n.createElement(f,o(o({ref:t},u),{},{components:a})):n.createElement(f,o({ref:t},u))}));function m(e,t){var a=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var i=a.length,o=new Array(i);o[0]=p;var l={};for(var s in t)hasOwnProperty.call(t,s)&&(l[s]=t[s]);l.originalType=e,l.mdxType="string"==typeof e?e:r,o[1]=l;for(var c=2;c<i;c++)o[c]=a[c];return n.createElement.apply(null,o)}return n.createElement.apply(null,a)}p.displayName="MDXCreateElement"},2984:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>s,contentTitle:()=>o,default:()=>d,frontMatter:()=>i,metadata:()=>l,toc:()=>c});var n=a(83117),r=(a(67294),a(3905));const i={title:"v0.2.4",slug:"/managed-datahub/release-notes/v_0_2_4",custom_edit_url:"https://github.com/datahub-project/datahub/blob/master/docs/managed-datahub/release-notes/v_0_2_4.md"},o="v0.2.4",l={unversionedId:"docs/managed-datahub/release-notes/v_0_2_4",id:"docs/managed-datahub/release-notes/v_0_2_4",title:"v0.2.4",description:"---",source:"@site/genDocs/docs/managed-datahub/release-notes/v_0_2_4.md",sourceDirName:"docs/managed-datahub/release-notes",slug:"/managed-datahub/release-notes/v_0_2_4",permalink:"/docs/managed-datahub/release-notes/v_0_2_4",draft:!1,editUrl:"https://github.com/datahub-project/datahub/blob/master/docs/managed-datahub/release-notes/v_0_2_4.md",tags:[],version:"current",frontMatter:{title:"v0.2.4",slug:"/managed-datahub/release-notes/v_0_2_4",custom_edit_url:"https://github.com/datahub-project/datahub/blob/master/docs/managed-datahub/release-notes/v_0_2_4.md"},sidebar:"overviewSidebar",previous:{title:"v0.2.5",permalink:"/docs/managed-datahub/release-notes/v_0_2_5"},next:{title:"v0.2.3",permalink:"/docs/managed-datahub/release-notes/v_0_2_3"}},s={},c=[{value:"Release Availability Date",id:"release-availability-date",level:2},{value:"Release Changelog",id:"release-changelog",level:2}],u={toc:c};function d(e){let{components:t,...a}=e;return(0,r.kt)("wrapper",(0,n.Z)({},u,a,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"v024"},"v0.2.4"),(0,r.kt)("hr",null),(0,r.kt)("h2",{id:"release-availability-date"},"Release Availability Date"),(0,r.kt)("p",null,"24-Mar-2023"),(0,r.kt)("h2",{id:"release-changelog"},"Release Changelog"),(0,r.kt)("hr",null),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"Since ",(0,r.kt)("inlineCode",{parentName:"li"},"v0.2.3")," no changes from OSS DataHub have been pulled in."),(0,r.kt)("li",{parentName:"ul"},"fix(ui) Safeguard ingestion execution request check - Fixes an error on frontend managed ingestion page"),(0,r.kt)("li",{parentName:"ul"},"fix(impactAnalysis): fix filtering for lightning mode search"),(0,r.kt)("li",{parentName:"ul"},"fix(search): fix tags with colons"),(0,r.kt)("li",{parentName:"ul"},"refactor(incidents): Remove dataset health caching to make incident health instantly update"),(0,r.kt)("li",{parentName:"ul"},"fix(ui): Address regression in column usage stats + add unit test"),(0,r.kt)("li",{parentName:"ul"},"fix(timeBasedLineage): fix ingestProposal flow for no ops"),(0,r.kt)("li",{parentName:"ul"},"feat(assertions + incidents): Support Querying Entities by Assertion / Incident Status + Chrome Embed Optimizations"),(0,r.kt)("li",{parentName:"ul"},"fix(lineage): change default lineage time window to All Time"),(0,r.kt)("li",{parentName:"ul"},"Truncate cache key for search lineage"),(0,r.kt)("li",{parentName:"ul"},"feat(config): Add endpoint to exact search query information"),(0,r.kt)("li",{parentName:"ul"},"fix(default policies): Add Manage Proposals Default Policies for Root User")))}d.isMDXComponent=!0}}]);