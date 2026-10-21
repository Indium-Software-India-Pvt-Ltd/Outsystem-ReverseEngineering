# Official OutSystems APIs and Interfaces for Reading/Exporting Application Model & Metadata

Research date: 2026-10-21. Covers OutSystems 11 (self-managed and OutSystems Cloud) and OutSystems Developer Cloud (ODC). Each section flags which platform applies.

---

## Q1: The OutSystems Model API (OutSystems.Model, OutSystems.Model.Reader, OutSystems.Common, OutSystems.ObjectKeys)

### Takeaway

As of 2026 the **OutSystems Model API is officially acknowledged and officially used** — it is the documented mechanism behind the Service Studio MCP server in OutSystems 11, with **read capabilities Generally Available and write capabilities in Beta**. However, it is *not* published as a standalone SDK: there is no NuGet package, and its class/method reference ships as Markdown files inside OutSystems' own MCP skill repository rather than on success.outsystems.com. The physical assemblies live in the Service Studio install folder (`OutSystems.Model.V1.dll` et al.) and are consumed by referencing a local Service Studio installation. This applies to **O11 only**; ODC has no equivalent local model API.

### Cited Findings

**Official existence and documentation**

- OutSystems' own O11 documentation states: "your MCP host connects to the Service Studio MCP server, a local MCP server that runs inside Service Studio on your machine. It writes C# code that uses the OutSystems Model API and sends that code to the Service Studio MCP server, which runs it on a copy of the module." — [OutSystems MCP in O11 and ODC](https://success.outsystems.com/documentation/11/outsystems_mcp/outsystems_mcp_in_o11_and_odc/)
- The Service Studio MCP server is started from Service Studio: "To work on a module with an AI agent, go to the Edit menu > MCP Server and start the Service Studio MCP server." — [Service Studio overview](https://success.outsystems.com/Documentation/11/Getting_started/Service_Studio_Overview/)
- OutSystems maintains a first-party, MIT-licensed repository of agent skills for this: `OutSystems/outsystems11-mcp`, described as "Skills that let Claude Code, GitHub Copilot, Cursor, Kiro and other coding agents work with OutSystems 11 apps via the Service Studio MCP server." — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp)
- The MCP server "ships in the standard release, so no separate build or activation is needed," requiring **Service Studio 11.55.91 or later**; it is started via **Edit > MCP Configuration...**, default port **41820**, HTTP endpoint **`http://127.0.0.1:41820/mcp`**. — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp)
- Registration example: `claude mcp add --transport http servicestudio http://127.0.0.1:41820/mcp --scope user` — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp)

**Support status (explicit)**

- Read tools are **Generally Available**; write tools are **Beta**. The skill describes the write set as "a non-final OutSystems capability provided to collect customer feedback," and instructs that the user be pointed at https://www.outsystems.com/legal/beta-features-agreement on first write use. — [servicestudio-mcp-oml/SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md); [repo README](https://github.com/OutSystems/outsystems11-mcp)
- Beta write behavior "may change between Service Studio releases." — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp)
- A community write-up summarises the posture as: "Writes are Beta. Reads are GA. Treat mutating capabilities as a strong accelerator inside a reviewed workflow, not as autonomous CI," and notes "the Model API doesn't cover everything." — [The OutSystems MCP Server: What It Actually Unlocks (itnext.io)](https://itnext.io/the-outsystems-mcp-server-what-it-actually-unlocks-995cdc7ed720)

**Namespaces and types (confirmed)**

- Allowed `imports` are restricted to `OutSystems.Model` and its sub-namespaces, e.g. `OutSystems.Model.Data`. The host auto-adds `OutSystems.Model.UI`, `OutSystems.Model.UI.Web` and `OutSystems.Model.UI.Mobile`. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Confirmed interface types: `IESpace`, `IServerEntity`, `IScreen`, `IWebScreen`, `IMobileScreen`, `IWebFlow`. Some short names are ambiguous and must be fully qualified, e.g. `OutSystems.Model.Logic.Nodes.IStartNode`. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- The programming contract: each unit of code is a full `eSpace => { … }` lambda; the parameter must be named `eSpace`; `eSpace.Save(...)` must not be called (the host adds it). — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)

**Assemblies and on-disk location (confirmed via third-party csproj)**

- The third-party `oml-cli` project references these assemblies directly, all rooted at an MSBuild property `SS` whose default value is `C:\Program Files\OutSystems\Service Studio 11\Service Studio`, with `Private="false"`:
  - `$(SS)\OutSystems.Model.V1.dll`
  - `$(SS)\OutSystems.Model.Plugins.dll`
  - `$(SS)\ServiceStudio.PluginAPI.dll`
  - `$(SS)\ServiceStudio.Framework.dll`
  - `$(SS)\ServiceStudio.Common.dll`
  - `$(SS)\SkiaSharp.dll`, `$(SS)\Svg.Skia.dll`, `$(SS)\Svg.Model.dll`, `$(SS)\ShimSkiaSharp.dll`
  - `$(SS)\Plugins\ServiceStudio\ServiceStudio.Plugin.NRWidgets.dll`
  - `$(SS)\Plugins\ServiceStudio\ServiceStudio.Plugin.RESTService.dll`
  — [OmlCli.Core.csproj](https://raw.githubusercontent.com/Topurrra/oml-cli/main/src/Core/OmlCli.Core.csproj)
- Target framework is **`net8.0`**; prerequisites are "Windows, Service Studio 11, and the .NET 8 runtime (the SDK to build from source)." — [OmlCli.Core.csproj](https://raw.githubusercontent.com/Topurrra/oml-cli/main/src/Core/OmlCli.Core.csproj); [oml-cli README](https://github.com/Topurrra/oml-cli)
- `oml-cli` "uses your locally installed Service Studio assemblies and does not ship them"; for non-default installs you set `OML_SERVICE_STUDIO` and build with `-p:SS="<that folder>"`. It "reads and changes `.oml` modules through the typed Model API of your installed Service Studio" and "never edits OML XML." It explicitly states it is "Not affiliated with OutSystems." — [oml-cli](https://github.com/Topurrra/oml-cli)

**What the Model API can read from an .oml (confirmed list)**

- Readable: "Entities, attributes, foreign keys, identifiers, structures, actions, screens, web blocks, roles, variables, settings, events, integrations, timers, exceptions, locales, images, resources, scripts, email templates, external sites, themes, and references via `eSpace.References.Named(...)`." — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Writable (Beta): "Entities, attributes, screens, server and client actions, structures, roles and integrations." — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Full MCP read tool set: `getDataModel`, `getStructures`, `getActionNames` (param `objectType`: server | client | service), `getServerAction`, `getClientAction`, `getServiceAction`, `getScreenNames`, `getScreen`, `getWebBlockNames`, `getWebBlock`, `getRoleNames`, `getRole`, `getClientVariables`, `getSessionVariables`, `getSettings`, `getEvents`, `getEventHandlers`, `getIntegrations`, `getTimers`, `getUserExceptions`, `getRoleExceptions`, `getLocales`, `getException`, `getImage`, `getResource`, `getScript`, `getEmailTemplate`, `getExternalSite`, `getTheme`, `getSerializedObject`, `getSerializedObjectByKey`, `getSerializedObjectByNameAndType`, `runQuery`, `getValidationMessages`, plus Traditional Web variants `getScreenNamesTraditional`, `getScreenTraditional`. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Session/host tools: `createSessionToken` (param `clientName`, shown in the Service Studio approval dialog; returns a token), `listApps` (param `sessionToken`; "returns the open module and its references, each with `moduleType`"). — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Write/lifecycle tools: `applyModelApiCode` (input `{ eSpaceName, code, imports }`; `imports` required, may be empty; returns `exceptionMessage`, `stdoutOutput`, `stderrOutput`, `validationMessages`, `mutatedOmlPath`), `omlMerge` (`eSpaceName`, `mutatedOmlPath` → `merged`), `omlReset` (`eSpaceName`), `omlRefreshReferences` (`eSpaceName` → `message`, `hasErrors`, `hasWarnings`), `omlPublish` (`eSpaceName` → `published`, `status`, `reason`, `messages`). — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- **ModelQL** is a dedicated query language exposed by `runQuery`; queries "must start with `Root { … }`". — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)

**Sandbox and limits (important for "reverse engineering" use)**

- Model API code cannot use `Console`, `System.`-qualified names, reflection, or file/process/network access; collection expressions (`[a, b]`) are rejected. Debug inspection is done by throwing an exception whose message begins with `PROBE:`. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- `applyModelApiCode` times out after **300 seconds**. Translations cannot be written. New external or cross-module dependencies cannot be added through the API (must be added in Service Studio first). Entity/attribute names may be silently renamed, and attribute names are truncated to **28 characters**. Mobile-bound reads return empty on Traditional Web modules. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Code-returning read tools require an `includeJson` field whose value must always be `"Never"` (host overrides it, but the field must be present). — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)

**Authentication / trust model**

- O11: no network credentials. Service Studio must have a module open and the MCP server started; on the first command Service Studio shows an access prompt establishing a "trust handshake." Approval is interactive and local. — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp)
- All writes are staged into Service Studio's interactive **Compare-and-Merge** window and must be accepted before entering the module; a "Write permissions" setting determines the flow. — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp); [OutSystems MCP in O11 and ODC](https://success.outsystems.com/documentation/11/outsystems_mcp/outsystems_mcp_in_o11_and_odc/)
- "The only network access the O11 setup needs is the host's own connection to its model provider." — [OutSystems MCP in O11 and ODC](https://success.outsystems.com/documentation/11/outsystems_mcp/outsystems_mcp_in_o11_and_odc/)

**Where the reference docs live**

- The Model API reference is *local files in the skill*, not an online docs site: `docs/` holds "namespace doc files with interface and method signatures," `examples/` holds "worked C# lambdas that can be used directly as `code`," and `reference/` holds `verb-reference.md` and `lambda-contract.md`. The skill explicitly notes there is no `getModelApiDoc` or `getModelApiExamples` tool — those folders *are* the reference. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)

**Internal OML format (secondary source)**

- A community/Medium article on the OutSystems model states the model has an in-memory representation (as C# class instances) and an XML-based persistent representation, and that the OML is a compressed file made of several fragments. — [OutSystems Language VS OutSystems Model (Medium)](https://medium.com/cesarafonso/outsystems-language-vs-outsystems-model-60505d8c857e)
- A long-standing community ask for a public OML API exists as an Idea. — [Idea - OML API / accessing data](https://www.outsystems.com/ideas/5948/oml-api-accessing-data/)
- A CVE-era advisory incidentally confirms that Service Studio "loads several DLLs from the same directory when a user opens a .oml file" (DLL hijacking, CVE-2022-47636, Service Studio ≤ 11.53.30). — [Exploit-DB 51678](https://www.exploit-db.com/exploits/51678)

### Inferences

- The practical, *supported* programmatic route to an .oml's structure in 2026 is: install Service Studio 11.55.91+, open the module, start the local MCP server, and drive the read tools (GA) over HTTP on 127.0.0.1:41820. This is first-party and documented; it is also inherently **single-module, interactive, Windows-desktop-bound** — it reads the module currently open in Service Studio, not a file sitting on a build server.
- Referencing `OutSystems.Model.V1.dll` directly from your own .NET 8 process (the `oml-cli` approach) is **undocumented-but-present**: the assemblies are real, stable enough that a community CLI depends on them, and OutSystems itself builds the MCP server on them — but OutSystems publishes no reference, no NuGet package, and no compatibility guarantee for direct assembly consumption. Treat it as at-your-own-risk, versioned to the exact Service Studio build.
- The `.V1` suffix on `OutSystems.Model.V1.dll` suggests OutSystems has versioned the model API surface deliberately, which is mildly encouraging for stability, but no public statement confirms a compatibility contract.
- Because the API refuses to add cross-module dependencies and reads only the open module plus `eSpace.References.Named(...)`, factory-wide dependency graphs must come from LifeTime/Discovery/Code Quality, not from the Model API.

### Gaps

- **`OutSystems.Model.Reader`, `OutSystems.Common`, and `OutSystems.ObjectKeys` were not confirmed.** None appeared in the `oml-cli` csproj references, in the OutSystems MCP docs, or in search results. They may exist as internal assemblies in the Service Studio folder (the csproj uses `MSBuildWarningsAsMessages=MSB3277`, which suppresses conflicting-assembly-version warnings and hints at a wider transitive set), but I found no citable source. Verifying requires directory-listing an actual Service Studio 11 install and/or ILSpy/dnSpy inspection.
- **No NuGet package for OutSystems.Model was found.** Searches surfaced nothing; both the official MCP server and `oml-cli` consume local install assemblies. I cannot cite a statement that no package exists, only that none was found.
- No public class-level reference for the Model API on success.outsystems.com was found — the only reference material is in the GitHub skill's `docs/` folder, which I did not enumerate file-by-file.
- Exact parameter schemas for each read tool (in `reference/verb-reference.md`) were not retrieved.
- Whether a Platform Server install (as opposed to Service Studio) also contains these assemblies was not determined.
- Licensing/entitlement for the MCP server and Model API (whether any edition gate applies) is not stated on any page I read.

---

## Q2: LifeTime API / LifeTime Deployment API (O11)

### Takeaway

The LifeTime API v2 is the **fully supported, documented REST surface** for factory-level metadata in O11: applications, modules, versions, environments, deployments, plus (new in v2) deployment zones, users, teams and roles. It is authenticated with a LifeTime service account token and scoped entirely by that account's LifeTime permissions. A downloadable Swagger definition makes it the best machine-readable contract of any surface in this report.

### Cited Findings

- Base URL: `<lifetime-domain>/lifetimeapi/rest/v2` over HTTPS. Example: for `example-lt.example.com/lifetime`, the base URL is `example-lt.example.com/lifetimeapi/rest/v2`. — [LifeTime API v2](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_api_v2/)
- Scope: "REST API for managing applications, modules, environments, and deployments." — [OutSystems APIs index](https://success.outsystems.com/documentation/11/reference/outsystems_apis/)
- v1 → v2: "Version 2 of the API adds support for deployment zones, users, teams, and roles." The official page carries **no deprecation notes**. — [LifeTime API v2](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_api_v2/)
- Permissions: "All API operations are limited to the permissions associated with the Service Account used to call it, as defined in LifeTime." For DB connection operations, permissions are set at the environment level. — [LifeTime API v2](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_api_v2/)
- Authentication is covered by a separate "REST API Authentication" article linked from the v2 page; the v2 page itself does not name the token header. — [LifeTime API v2](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_api_v2/)
- Service account tokens are shown **only once** by LifeTime when generated. — [LifeTimeAPIConnector / Forge component guidance](https://www.outsystems.com/forge/component-documentation/25715/crosslifetimepromotion-o11)
- Machine-readable contract: "A Swagger file for v2 is available from the Downloads area for LifeTime 11.5.0 and later. It is the most complete source for endpoints, methods, and paths." The API is also available as a Postman collection. — [LifeTime API v2](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_api_v2/)
- A live Swagger definition is served per-instance at `https://<LIFETIMEURL>/lifetimeapi/rest/v2/swagger.json`. — [CrossLifeTimePromotion O11 documentation](https://www.outsystems.com/forge/component-documentation/25715/crosslifetimepromotion-o11)
- Confirmed endpoint shape for version metadata: `GET /applications/{ApplicationKey}/versions/`. — [OutSystems forum: API](https://www.outsystems.com/forums/discussion/84437/api/)
- Cross-infrastructure deployment (binary upload of an `.oap`) is a documented v2 capability and requires **LifeTime 11.22.0 or later**. — [CrossLifeTimePromotion O11](https://www.outsystems.com/forge/component-documentation/25715/crosslifetimepromotion-o11)
- Known limitation: "there is no built-in capability to programmatically untick or skip republishing dependent applications in the v2 API," and direct database edits are not supported. — [OutSystems forum: unticking dependent applications via LifeTime API](https://www.outsystems.com/forums/discussion/102470/unticking-dependent-applications-via-lifetime-api/)
- OutSystems publishes a dedicated examples page. — [LifeTime Deployment API examples](https://www.outsystems.com/product-updates/lifetime-deployment-api-examples)
- Two adjacent supported surfaces exist alongside the REST API:
  - **LifeTime Services API** — "SOAP services for managing the infrastructure." — [LifeTime Services API](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_services_api/)
  - **LifeTime SDK** — "Extends LifeTime, including building plug-ins." — [LifeTime SDK](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_sdk/)

### Inferences

- For factory-level reverse engineering (what apps/modules exist, their versions, which environments they are in, team ownership), LifeTime API v2 is the correct and fully supported starting point, and pulling `swagger.json` from the target instance is the most reliable way to enumerate the real endpoint set for that exact LifeTime version rather than relying on docs.
- LifeTime gives you the *inventory and topology*; it does not give you intra-module logic. Combining LifeTime (inventory) + Model API via Service Studio MCP (per-module internals) + Code Quality/Discovery (dependency graph and quality findings) is the complete supported stack.
- Because every operation is bounded by the service account's LifeTime permissions, a read-only reverse-engineering service account should be granted only view-level permissions across environments.

### Gaps

- The full enumerated endpoint list with methods, paths and response field schemas was **not retrievable from the public docs page** — OutSystems defers it to the downloadable Swagger file (requires a LifeTime 11.5.0+ Downloads-area entitlement) or an instance's own `swagger.json` (requires an authenticated LifeTime instance). I could not fetch either.
- The exact authentication header name/format (the "REST API Authentication" article) was not fetched; only that a service account token is used.
- Whether LifeTime API v2 exposes **inter-application/module dependency** data (as opposed to just version/deployment data) was not confirmed from any source I read.
- LifeTime API v1's status (still live, soft-deprecated?) is unconfirmed; the v2 page carries no deprecation statement, and I found no explicit v1 end-of-life notice.

---

## Q3: ODC (OutSystems Developer Cloud) APIs, ODC CLI, ODC Portal APIs

### Takeaway

ODC has a **fully supported, OAuth 2.0 / OIDC-authenticated public REST API family spanning 12 functional domains**, several of which are directly relevant to model/metadata extraction: Portfolio (deployed assets per environment), Dependency (impact analysis and dependency data), Asset repository (asset info and revisions), and Code Quality (findings and quality scores). ODC also has an OutSystems-hosted remote MCP server, unlike O11's local one. I found no evidence of a documented ODC CLI.

### Cited Findings

**API catalogue** — the ODC public REST APIs overview names 12 domains (version inferred from reference filenames):

| Domain | Purpose (per OutSystems) | Reference doc | Version |
|---|---|---|---|
| User and access management | Manage end-users, access, groups, access policies | `identity-v1.md` | v1 |
| **Portfolio management** | **View deployed assets in each environment** | `portfolio-v2.md` | **v2** |
| Build operations | Start builds and monitor build status | `build-v1.md` | v1 |
| Native mobile builds | Manage iOS/Android configs, check whether a build is needed, run builds, get download links | `native-mobile-builds-api-v1.md` | v1 |
| Deployments | Deploy assets to stages, track deployment progress | `deployment-v1.md` | v1 |
| **Dependency management** | **Run impact analysis and retrieve dependency data** | `dependency-v1.md` | v1 |
| **Asset repository** | **Access asset information and manage revisions** | `asset-v1.md` | v1 |
| Asset configurations | Manage global environment settings and per-asset configuration | `asset-config-v1.md` | v1 |
| Environment configurations | Manage IP filters, private gateways, custom domains | `env-config-v1.md` | v1 |
| External library generation | Generate and manage external libraries from .NET packages | `external-library-generation-api-v1.md` | v1 |
| **Code quality** | **Submit analyses and retrieve findings and quality scores** | `code-quality-api-v1.md` | v1 |
| Subscription | Access subscription metrics and end-user capacity usage | `subscription-v1.md` | v1 |

— [ODC public REST APIs overview](https://github.com/OutSystems/docs-odc/blob/main/src/eap/reference/apis/public-rest-apis/overview.md)

- There is **no separate "App API"** in ODC; the nearest equivalent is Build operations. The overview also references CI/CD API use cases (`ci-cd-apis-use-cases/analyze-deployment-impact.md`) but not as a separate domain. — [ODC public REST APIs overview](https://github.com/OutSystems/docs-odc/blob/main/src/eap/reference/apis/public-rest-apis/overview.md)
- API style: "RESTful, accept form-encoded request bodies, return JSON, and use standard HTTP status codes and verbs." — [ODC public REST APIs overview](https://github.com/OutSystems/docs-odc/blob/main/src/eap/reference/apis/public-rest-apis/overview.md)

**Authentication**

- Authentication uses **OpenID Connect, built on OAuth 2.0**. — [ODC public REST APIs overview](https://github.com/OutSystems/docs-odc/blob/main/src/eap/reference/apis/public-rest-apis/overview.md)
- You need a **client ID and client secret from an API Client created in the ODC Portal**; creating the API client creates an API account and generates the credentials. — [Using OAuth 2.0 to access the APIs](https://success.outsystems.com/documentation/outsystems_developer_cloud/odc_rest_apis/api_authentication_and_authorization/using_oauth_2_0_to_access_the_apis/); [ODC REST APIs getting started](https://success.outsystems.com/documentation/outsystems_developer_cloud/odc_rest_apis/getting_started/)
- Example authenticated call: `GET /api/identity/v1/users` on the portal domain, with a Bearer access token in the `Authorization` header. — [ODC REST APIs getting started](https://success.outsystems.com/documentation/outsystems_developer_cloud/odc_rest_apis/getting_started/)
- The OIDC discovery document at `<portal-domain>/identity/.well-known/openid-configuration` lists the token endpoint. *(Third-party source — verify against official docs.)* — [OutSystems ODC Rest APIs (Medium)](https://medium.com/@neves.sousa/outsystems-odc-rest-apis-unlocking-limitless-integration-possibilities-913f875cacfd)
- Permissions are granular per asset/stage: a Forge demo notes "access to the stage's assets is required. Checking for example Edit Asset Configurations accomplishes this." — [ODC API Demo (ODC) Forge](https://www.outsystems.com/forge/component-documentation/23456/odc-api-demo-odc/0)

**Release timeline**

- Dec 2024: ODC introduced API Clients plus the User and Access Management API and the Portfolio API — "They allow customers to create and manage API Clients, which allows them to call REST APIs from different functional domains." — [ODC REST APIs product update](https://www.outsystems.com/fr-fr/product-updates/odc-rest-apis/)
- Environment config + Subscription APIs: "It allows you to manage environment configurations to automate IP Filters, Private Gateways, and Custom Domains," and a Subscription API exposing "the same metrics shown in the Subscription Overview." — [ODC DevOps APIs: env config and subscription metrics](https://www.outsystems.com/product-updates/odc-devops-apis-env-config-and-subscription-metrics)
- **22 Dec 2025**: asset-creation and external-library lifecycle DevOps APIs — "These new DevOps APIs enable you to integrate asset creation directly into your portfolio approval process, whether in OutSystems or a third-party tool." — [ODC APIs: asset creation and external libraries lifecycle](https://www.outsystems.com/product-updates/odc-apis-asset-creation-and-external-libraries-lifecycle)

**ODC MCP server**

- ODC's MCP server is "a remote server that OutSystems hosts for your tenant. You sign in with your ODC identity. Every call reaches the OutSystems cloud." In ODC "the agent works across the tenant and the full app lifecycle. It can also build an app in an empty tenant." Changes follow the ODC lifecycle and audit trail; before a publish, deploy or rollback "the agent restates the operation and waits for confirmation." — [OutSystems MCP in O11 and ODC](https://success.outsystems.com/documentation/11/outsystems_mcp/outsystems_mcp_in_o11_and_odc/)
- A Forge-listed "MCP Server (ODC)" component also exists. — [MCP Server (ODC) Forge](https://www.outsystems.com/forge/component-documentation/21830/mcp-server-odc)

### Inferences

- For ODC, the Portfolio v2 + Dependency v1 + Asset v1 trio is the sanctioned metadata-extraction path and is strictly *factory/portfolio level* — it tells you what assets exist, their revisions, and how they depend on each other, but nothing published indicates it returns intra-module logic (screens, action flows). ODC appears to have **no public per-module model-reading API equivalent to O11's Model API**; the ODC MCP server is the closest analogue and it is cloud-mediated, not an inspectable file/assembly surface.
- Portfolio being at **v2** while everything else is v1 suggests it is the most-iterated and most-consumed domain.
- The ODC auth model (per-tenant API Client with granular asset/stage permissions) is materially better for least-privilege automation than O11's single LifeTime service-account token.

### Gaps

- **No base URLs, URL path patterns, scopes, or rate limits** are stated on the ODC overview page; those live in the individual reference pages, which I did not fetch. The only concrete path confirmed anywhere is `/api/identity/v1/users`.
- **I found no documented ODC CLI.** Searches returned only Forge components (Console Web API, ODC Web Utilities) and O11-era tools (ExecuteProcessUtility, ScriptCLI). I cannot confirm whether an official ODC CLI exists in 2026. This is a genuine unknown, not a negative finding.
- Whether ODC exposes any downloadable module/app source artifact (an .oml/.oap equivalent) was not determined. ODC's architecture is cloud-native with no documented local module file in anything I read.
- Exact field schemas returned by Portfolio v2, Dependency v1 and Asset v1 are unknown.

---

## Q4: Service Center metadata APIs and OML download endpoints (O11)

### Takeaway

Downloading an `.oml` is officially supported through **UI paths only** — Service Center's module page has a "Download Published Version" button, and Service Studio has Module > Export > Save As. I found **no documented HTTP URL pattern** for scripted .oml download, and no documented Service Center REST/SOAP API for factory metadata (Service Center does not appear in OutSystems' API reference index at all).

### Cited Findings

- Official support path: open the module in Service Studio, pick **Module Management** from the Module menu, which opens the module's details page in Service Center under the Factory section; on that page "click the **Download Published Version** button." — [Sharing a project (OutSystems Support)](https://success.outsystems.com/support/forge_components/forge_faqs/sharing_a_project/)
- Alternative: in Service Studio, "click the Module menu and select the **Export > Save As...** option." — [Sharing a project](https://success.outsystems.com/support/forge_components/forge_faqs/sharing_a_project/)
- Community confirmation that modules can be located via Service Center's Modules page and downloaded there. — [OutSystems forum: Module download](https://www.outsystems.com/forums/discussion/59366/module-download/); [How to generate an OML file?](https://www.outsystems.com/forums/discussion/56928/how-to-generate-an-oml-file/)
- Service Center / `/ServiceCenter` does **not** appear in the OutSystems 11 APIs reference index, which documents 30 APIs across 13 categories (BPT, Charts, client-side, Database, Emails, End User Management, Infrastructure/IT Users Management, Integration, Monitoring, Scripting, System Actions, Security, Text, Code Quality). — [OutSystems APIs index](https://success.outsystems.com/documentation/11/reference/outsystems_apis/)
- Relatedly, LifeTime API v2 *does* support binary upload/download of `.oap` application packages for cross-infrastructure deployment (LifeTime 11.22.0+) — this is the documented programmatic binary-artifact path, at the **application** (.oap) rather than **module** (.oml) level. — [CrossLifeTimePromotion O11](https://www.outsystems.com/forge/component-documentation/25715/crosslifetimepromotion-o11)

### Inferences

- The sanctioned programmatic route to a *binary application artifact* is LifeTime API v2's `.oap` operations, not a Service Center .oml URL. An `.oap` is an application package containing modules, so for pipeline-based reverse engineering this is the supportable acquisition path: pull the `.oap` via LifeTime API v2, unpack to get `.oml` modules, then read each `.oml` via Service Studio + Model API.
- Scripting the Service Center "Download Published Version" button would require session-cookie scraping of an undocumented ASP.NET endpoint — this is unsupported and likely to break across Platform Server versions. It should be classified at-your-own-risk.

### Gaps

- **No citable URL pattern for .oml download over HTTP.** None of the official or community sources I read gave one. Determining it requires inspecting an authenticated Service Center instance's network traffic.
- Whether Service Center exposes any SOAP/REST metadata endpoint at all is unconfirmed; its absence from the APIs index is suggestive but not a positive statement.
- Permissions required for the Service Center download (presumably a factory/developer role) were not stated by any source I read.

---

## Q5: Discovery and Architecture Dashboard / AI Mentor Studio / Code Quality

### Takeaway

The tool has been renamed twice — **Architecture Dashboard → AI Mentor Studio → Code Quality** — and its API has correspondingly moved from `ArchitectureDashboardAPI` (removed after 31 Dec 2024) to `AIMentorStudioAPI` to the current **Code Quality API**, which is documented and supported in both O11 and ODC. It collects platform metamodel data plus module and dependency information, and can optionally ingest Discovery snapshot data. Findings are exportable (there is a distinct "Export findings" permission and a documented Excel export).

### Cited Findings

**Naming and API migration**

- "Architecture Dashboard was renamed to AI Mentor Studio and it is now part of the OutSystems AI Mentor System." — [Architecture Dashboard Is Now AI Mentor Studio](https://www.outsystems.com/product-updates/ai-mentor-studio/)
- The current docs page states flatly: "**AI Mentor Studio is now Code Quality.**" — [How does AI Mentor Studio / Code Quality work](https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/how_does_ai_mentor_studio_work/)
- Release 1.33 scheduled removal of the `ArchitectureDashboardAPI` name after **31 December 2024**: "Customers still using this API must change the address of their integrations to `AIMentorStudioAPI`, which has the exact same behavior and functionality." — [AI Mentor Studio release notes](https://success.outsystems.com/support/release_notes/ai_mentor_studio/)
- The O11 API index now lists a **Code Quality API**: "Retrieves technical debt data by app, team, and category for CI/CD and BI integration." — [Code Quality API](https://success.outsystems.com/documentation/11/reference/outsystems_apis/code_quality_api/); [OutSystems APIs index](https://success.outsystems.com/documentation/11/reference/outsystems_apis/)
- ODC has an equivalent domain: code quality — "Submit analyses and retrieve findings and quality scores" (`code-quality-api-v1.md`). — [ODC public REST APIs overview](https://github.com/OutSystems/docs-odc/blob/main/src/eap/reference/apis/public-rest-apis/overview.md)

**What metadata it extracts (directly relevant to reverse engineering)**

- Collected data includes: platform metamodel data — "infrastructure activation code, environment names and Platform Server versions, teams, apps and modules (names and identifiers), and platform configurations"; plus "modules and dependency information for code analysis"; plus, with user agreement at setup, user name/username/email/creation and last-login dates/LifeTime permissions; plus **optionally "discovery snapshot data (architectural references, applications, and modules) for architecture analysis."** — [How does Code Quality work](https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/how_does_ai_mentor_studio_work/)
- Collection mechanism: a **Code Quality LifeTime Plugin** installed in the platform installation uses **environment probes**; plugin and SaaS exchange binary data over a well-known HTTPS endpoint; IP/DNS addresses are not transmitted; only default ports are needed; a forward proxy can be used. With OutSystems account authentication the plugin always initiates communication; with IT User authentication communication is bidirectional. — [How does Code Quality work](https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/how_does_ai_mentor_studio_work/)

**Permissions / entitlement**

- Permission "**Manage Code Quality API**" requires **Change and Deploy Applications** or **Full Control** for the code-analysis environment. — [How does Code Quality work](https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/how_does_ai_mentor_studio_work/)
- A separate "**Export findings**" permission exists; other permissions cover ignoring modules, enabling AI auto-classification, and overriding module auto-classification. — [How does Code Quality work](https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/how_does_ai_mentor_studio_work/)
- Access is also moderated per app: "Except in cases where the permission level of a specific app (or teams assigned to that app) is set lower than that assigned to a role or team." — [Getting started with AI Mentor Studio](https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/getting_started_with_ai_mentor_studio/)

**Export and known API defects**

- Excel export exists; release 1.20 "Fix a bug on the export to excel that was returning duplicated lines when the list had more than 1000 records to export." — [AI Mentor Studio release notes](https://success.outsystems.com/support/release_notes/ai_mentor_studio/)
- Release 1.33 "Fixed an issue from a recent change that caused the API to return incorrect information for application related findings" — the API had returned duplicate copies of a pattern instead of one entry per pattern; module-level findings were unaffected. — [AI Mentor Studio release notes](https://success.outsystems.com/support/release_notes/ai_mentor_studio/)

**Discovery**

- Discovery is a Forge component for analyzing and improving factory architecture. — [Discovery Forge overview](https://www.outsystems.com/forge/component-overview/1770/overview-o11)
- Application Layer Definitions can be imported from Discovery into other tooling. — [Discovery Forge overview](https://www.outsystems.com/forge/component-overview/1770/overview-o11)
- The community distinguishes the two tools' roles explicitly. — [Discovery VS Architecture Dashboard (AI Mentor Studio)?](https://www.outsystems.com/forums/discussion/84754/discovery-vs-architecture-dashboard-ai-mentor-studio-which-one-is-more-import/)

### Inferences

- Code Quality's data collection is the single best *documented* description of what OutSystems itself considers extractable application metadata: platform metamodel + module and dependency information + Discovery architectural references. If OutSystems' own analysis product is built on those three inputs, they are the right targets for any reverse-engineering effort.
- Because Code Quality is a SaaS that *uploads* your metamodel and dependency data, the Code Quality API is effectively a supported way to read back a normalized dependency/quality view of your factory without touching OSSYS_ tables — an attractive supported alternative to direct DB querying.
- Discovery is a **Forge component**, i.e. community-governed and not a supported product API; its value here is as a data source Code Quality can ingest, and as a factory dependency analyzer whose own database is a de facto (unsupported) dependency graph.
- The twice-renamed API (ArchitectureDashboardAPI → AIMentorStudioAPI → Code Quality API) is a concrete precedent that even *supported* OutSystems metadata APIs get renamed with hard cutover dates. Any integration should pin to the current name and watch release notes.

### Gaps

- **Code Quality API endpoints, authentication specifics, and response schemas were not retrieved.** The docs page I read lists "Code Quality API" and "Code Quality API authentication" in its navigation without detail; I did not fetch those pages.
- Whether findings are exportable *via the API* as opposed to only via Excel in the UI is not explicitly stated; the existence of both an "Export findings" permission and a findings-returning API strongly implies yes, but I have no direct quote.
- Licensing/entitlement for Code Quality (it is a SaaS add-on; whether all O11 editions include it) was not stated on any page I read. This is likely a commercial gate and should be verified.
- Supported O11 Platform Server versions for the Code Quality plugin are not listed; the page only notes the plugin collects each environment's Platform Server version.
- Discovery's own schema/export surface and whether it has an API were not researched in depth.
- The post-2024 status of the `ArchitectureDashboardAPI` address is unconfirmed (the deadline passed; presumably dead, but no source states it is now returning errors).

---

## Q6: Platform metamodel database tables (OSSYS_*) — O11

### Takeaway

OutSystems **officially documents the existence and classification** of the metamodel tables and states that system (`OSSYS_`) entities are **read-only — writing to them is prohibited** — but it does **not** publish a column-level reference, and the only table whose contents are described is OSSYS_ENTITY. Reading them is therefore best characterized as *documented-at-the-table-name-level, unsupported at the schema level*. The Forge "Extended Metamodel" component, which many teams use for this, openly states it relies on private, undocumented APIs and is not supported by OutSystems.

### Cited Findings

**Official classification**

- Three entity classes:
  - **System entities** — `OSSYS_` prefix, "form the platform's metamodel… should be used only to read, and… writing to them is **prohibited** to protect platform integrity."
  - **Application entities** — `OSUSR_` prefix, hold business data; may be read and written in migration except static entity data referenced as foreign keys.
  - **Hybrid entities** — platform-managed but written by applications at runtime; need extra care; categories are Users, BPT process instances, BPT activity instances, BPT events, and Emails.
  — [OutSystems Platform Metamodel](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)
- Officially listed **metamodel** tables (the list is explicitly marked incomplete): `OSSYS_APP_DEFINITION_MODULE`, `OSSYS_APPLICATION`, `OSSYS_BPM_ACTIVITY_DEFINITION`, `OSSYS_BPM_ACTIVITY_OUTPUT_DEF`, `OSSYS_BPM_EVENT`, `OSSYS_BPM_EVENT_QUEUE`, `OSSYS_BPM_PROCESS_DEFINITION`, `OSSYS_BPM_PROCESS_INPUT_DEF`, `OSSYS_BPM_PROCESS_OUTPUT_DEF`, `OSSYS_ENTITY`, `OSSYS_ENTITY_ATTR`, `OSSYS_ENTITY_RECORD`, `OSSYS_ESPACE`, `OSSYS_ESPACE_ENTITY`, `OSSYS_ESPACE_TENANT`. — [OutSystems Platform Metamodel](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)
- Officially listed **application settings** tables: `OSSYS_CYCLIC_JOB`, `OSSYS_CYCLIC_JOB_SHARED`, `OSSYS_META_CYCLIC_JOB`, `OSSYS_SITE_PROPERTY`, `OSSYS_TENANT`, `OSSYS_WEB_REFERENCE`, `OSSYS_WEB_SERVICE`. — [OutSystems Platform Metamodel](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)
- The **only** content description given: `OSSYS_ENTITY` "holds the mapping between physical and logical entity names." Other tables are grouped by purpose (factory support, application support, engine and configuration) without content descriptions. — [OutSystems Platform Metamodel](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)

**OSSYS_ESPACE specifics (official)**

- `OSSYS_ESPACE` is "the table for Espaces defined in Service Studio. Older and deleted Espaces are kept but marked inactive." Tables that **consume** it include `OSSYS_ENTITY` and `OSSYS_ESPACE_ENTITY`; its **producers** include `OSSYS_ESPACE_VERSION` and `OSSYS_DBCATALOG`. — [Factory Application Modules](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/factory_application_modules/)
- Key semantics: "each Espace's `SS_Key` is unique across environments, but other keys such as entity keys are not, so you must pair them with the Espace key when comparing"; "The Espace / Extension always have a unique SS_Key generated and stored in the metamodel." — [Factory Application Modules](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/factory_application_modules/)
- Related official page for identity/role reconstruction: — [Application Users Groups and Roles](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/application_users_groups_and_roles/)
- Community confirmation that eSpace and eSpace-version records live in `OSSYS_ESPACE` / `OSSYS_ESPACE_VERSION`. — [Database tables for where eSpace versions are stored](https://www.outsystems.com/forums/discussion/62870/database-tables-for-where-espace-versions-are-stored/)

**Support posture**

- The official metamodel page sets rules for *data migration* (system entities read-only, hybrid writable under conditions) but **does not state whether querying these tables for analysis is supported**. — [OutSystems Platform Metamodel](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)
- A third-party consultancy notes that "several of the entities mentioned above are undocumented and are not recommended for use by OutSystems." — [OutSystems AOs: Keeping costs under control with automation (Rutabaga Technology)](https://www.rutabagatechnology.net/outsystems-aos-keeping-costs-under-control-with-automation/)

**Forge "Extended Metamodel" component**

- It "provides access to OutSystems metamodel entities," "relies on private and undocumented Platform APIs, so it may break when the Platform is upgraded," version **2.2.6** is compatible with OutSystems 11, and it "is not supported by OutSystems." — [Extended Metamodel (O11) Forge](https://www.outsystems.com/forge/component-overview/2146/extended-metamodel-o11)
- It exposes internal tables such as `REST_Expose` and `REST_Web_Reference`. A former OutSystems staff member said the configuration tables are not public because they are slated for a rewrite: "configurations are on the roadmap to be rewritten, and most configuration tables are likely to be modified or removed in the next majors." — [[Extended Metamodel] ExtendedMetamodel forum thread](https://www.outsystems.com/forums/discussion/95091/extended-metamodel-extendedmetamodel/)
- It exposes the app-to-Forge mapping as `App_Forge`, which the platform's System extension does not expose: "it isn't exposed through the System extension, but the Extended MetaModel Forge asset does expose it as App_Forge." — [Display which application has dependency of how many forge components](https://www.outsystems.com/forums/discussion/89276/display-which-application-has-dependency-of-how-many-forge-components/)
- The component has a documented history of fragility. — [[Extended Metamodel] Very fragile component](https://www.outsystems.com/forums/discussion/23080/extended-metamodel-very-fragile-component/)

### Inferences

- Reconstructable from the officially-named tables alone: the application/module inventory (`OSSYS_APPLICATION`, `OSSYS_APP_DEFINITION_MODULE`, `OSSYS_ESPACE`), the version history (`OSSYS_ESPACE_VERSION`), the full data model with physical↔logical name mapping (`OSSYS_ENTITY`, `OSSYS_ENTITY_ATTR`, `OSSYS_ESPACE_ENTITY`, `OSSYS_DBCATALOG`), static entity records (`OSSYS_ENTITY_RECORD`), BPT process and activity definitions (`OSSYS_BPM_*`), multi-tenancy (`OSSYS_TENANT`, `OSSYS_ESPACE_TENANT`), settings (`OSSYS_SITE_PROPERTY`), timers (`OSSYS_CYCLIC_JOB`, `OSSYS_META_CYCLIC_JOB`) and exposed/consumed SOAP (`OSSYS_WEB_SERVICE`, `OSSYS_WEB_REFERENCE`). That is a substantial structural picture — but notably **not** screen definitions or action logic, which remain Model-API-only.
- The correct way to characterize this surface: **table names are documented; schemas are not; reads are tolerated and implicitly expected (the docs say "use only to read"); writes are prohibited; and anything beyond the named list is undocumented.**
- The OutSystems staffer's statement that configuration tables are on a rewrite roadmap is the strongest available signal that a DB-level reverse-engineering tool will incur maintenance cost across major versions. Prefer the Model API / LifeTime API / Code Quality API where they cover the need.
- The platform's own **System extension** (the supported in-app reference giving access to some system entities) is the sanctioned subset; Extended Metamodel exists precisely to reach past it, which is why it is unsupported.

### Gaps

- **`OSSYS_MODULE`, `OSSYS_ESPACE_REFERENCE` and `OSSYS_APP_DEFINITION` were not confirmed** by any source I read. The official list has `OSSYS_APP_DEFINITION_MODULE` (not `OSSYS_APP_DEFINITION`) and `OSSYS_ESPACE_ENTITY` (not `OSSYS_ESPACE_REFERENCE`). `OSSYS_MODULE` did not appear in any official source; O11 historically calls modules "eSpaces" at the DB level, so `OSSYS_ESPACE` is likely the real table and `OSSYS_MODULE` may not exist. **This should be verified against a live database before being asserted.**
- **No column-level reference for any OSSYS_ table exists in public documentation**, including OSSYS_ESPACE. OutSystems documents table names and relationships but not schemas.
- The table that stores **module-to-module reference/dependency edges** was not identified from official docs. This is the single most important gap for dependency-graph reconstruction from the DB. (Discovery and the Code Quality API both clearly derive such a graph, so the data exists somewhere.)
- No official statement was found that says "querying OSSYS_ tables read-only for analysis is supported." The closest is the migration guide's "should be used only to read."
- Forge components named "**Metamodel**", "**OMLResource**" and "**Database Metamodel**" were **not found**. Only "Extended Metamodel" surfaced. "OMLResource" returned no results in any search; I cannot confirm it exists.
- Whether ODC has any equivalent queryable metamodel is unknown (ODC is cloud-native with no customer DB access documented).

---

## Q7: Integration Studio, extensions, .xif files; export-to-XML and documentation generators

### Takeaway

This area is **substantially under-researched in my pass** and I am flagging it rather than guessing. What I can report: the OutSystems Model API exposes `getIntegrations` and can read/write "integrations," the Forge "Extended Metamodel" exposes REST exposure/consumption tables, and community extensions (OML2XML) exist for XML conversion but are early-stage. I found no official export-to-XML path.

### Cited Findings

- The Model API's readable element list includes "integrations," and `getIntegrations` is one of the GA read tools; integrations are also in the Beta writable set. — [SKILL.md](https://raw.githubusercontent.com/OutSystems/outsystems11-mcp/main/servicestudio-mcp-oml/SKILL.md)
- Service Studio ships REST and widget plugins as separate assemblies: `Plugins\ServiceStudio\ServiceStudio.Plugin.RESTService.dll` and `Plugins\ServiceStudio\ServiceStudio.Plugin.NRWidgets.dll`, referenced alongside `ServiceStudio.PluginAPI.dll`. — [OmlCli.Core.csproj](https://raw.githubusercontent.com/Topurrra/oml-cli/main/src/Core/OmlCli.Core.csproj)
- Extended Metamodel exposes `REST_Expose` and `REST_Web_Reference` tables for REST integration metadata. — [[Extended Metamodel] ExtendedMetamodel](https://www.outsystems.com/forums/discussion/95091/extended-metamodel-extendedmetamodel/)
- Official metamodel tables cover SOAP integrations: `OSSYS_WEB_SERVICE` and `OSSYS_WEB_REFERENCE`. — [OutSystems Platform Metamodel](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)
- An **OML2XML** extension exists in the community that "converts an OML into XML that can be inspected," described in forum discussion as an OML API, "still at an early stage." — [Read and Display OML File as Text](https://www.outsystems.com/forums/discussion/96092/read-and-display-oml-file-as-text/); [OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/)
- An older forum consensus (circa 2018) held that "the only supported way to open an OML is through Service Studio." — [Can I see the source code of .oml file](https://www.outsystems.com/forums/discussion/76283/can-i-see-the-source-code-of-oml-file/); [Inspect the OML file](https://www.outsystems.com/forums/discussion/5476/inspect-the-oml-file/)
- Documentation generation is listed among the OutSystems MCP skill's own example prompts, alongside dependency mapping, risk flagging (security, performance, compliance), and dead-code/test-coverage analysis — i.e. OutSystems positions doc generation as a Model API use case rather than shipping a generator. — [OutSystems/outsystems11-mcp](https://github.com/OutSystems/outsystems11-mcp)
- Academic work exists on bidirectional transformation of the OutSystems model: CHAMELEON. — [CHAMELEON: OutSystems Live Bidirectional Transformations (arXiv)](https://arxiv.org/pdf/2305.03361)

### Inferences

- There is no official export-to-XML path. The supported substitute in 2026 is to drive the Model API's read tools (or `getSerializedObject*`) and serialize to your own format — which is effectively what OutSystems' own documentation-generation example prompt does.
- `getSerializedObject`, `getSerializedObjectByKey` and `getSerializedObjectByNameAndType` are the most promising Model API verbs for bulk/structural export, since "serialized object" implies a generic dump of a model element rather than a curated view. Worth investigating as the backbone of any extraction pipeline.
- Integration/extension metadata is split across surfaces: *definitions* via the Model API (`getIntegrations`), *factory-wide SOAP inventory* via official OSSYS_WEB_* tables, and *factory-wide REST inventory* only via the unsupported Extended Metamodel.

### Gaps

- **`.xif` files were not researched.** I have no citable findings on what an .xif contains, whether it can be read programmatically, or whether Integration Studio exposes any API or SDK. This is an open item and should be assigned to a follow-up pass.
- **Integration Studio's own extensibility surface** (plugin API, command line, project file format) is unknown to me.
- **No Forge documentation-generator components were identified by name.** My Forge searches returned Extended Metamodel and Discovery but no doc generator. I did not search Forge directly for "documentation generator"; this is a gap, not a negative finding.
- The OML2XML extension's identity (author, Forge URL, O11 compatibility, current status) was not pinned down; it is referenced only in forum discussion.
- Whether `getSerializedObject*` produces XML, JSON, or a proprietary format is unknown.

---

## Cross-cutting summary: support status by surface

| Surface | Platform | Support status | Auth | Gives you |
|---|---|---|---|---|
| **Service Studio MCP server — read tools** | O11 (SS 11.55.91+) | **Supported, GA** ([src](https://github.com/OutSystems/outsystems11-mcp)) | Local interactive approval prompt; `createSessionToken` | Full intra-module model: entities, attributes, FKs, structures, actions, screens, blocks, roles, variables, settings, events, integrations, timers, exceptions, locales, resources, themes, references |
| **Service Studio MCP server — write tools** | O11 (SS 11.55.91+) | **Beta** (beta-features agreement) ([src](https://github.com/OutSystems/outsystems11-mcp)) | same | Mutate entities/attrs/screens/actions/structures/roles/integrations via staged Compare-and-Merge |
| **Direct reference to `OutSystems.Model.V1.dll`** | O11, Windows, .NET 8 | **Undocumented-but-present; at-your-own-risk** ([src](https://raw.githubusercontent.com/Topurrra/oml-cli/main/src/Core/OmlCli.Core.csproj)) | n/a (local file) | Same model surface, scriptable; no OutSystems reference docs or compat guarantee |
| **LifeTime API v2** | O11 | **Supported** ([src](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_api_v2/)) | LifeTime service account token; permissions = that account's | Applications, modules, versions, environments, deployments, deployment zones, users, teams, roles; `.oap` binary up/download (LT 11.22.0+) |
| **LifeTime Services API (SOAP)** | O11 | **Supported** ([src](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_services_api/)) | LifeTime | Infrastructure management |
| **LifeTime SDK** | O11 | **Supported** ([src](https://success.outsystems.com/documentation/11/reference/outsystems_apis/lifetime_sdk/)) | n/a | Build LifeTime plug-ins |
| **Code Quality API** (ex-AIMentorStudioAPI, ex-ArchitectureDashboardAPI) | O11 + ODC | **Supported**; predecessor name removed after 31 Dec 2024 ([src](https://success.outsystems.com/support/release_notes/ai_mentor_studio/)) | "Manage Code Quality API" perm → needs Change&Deploy or Full Control on the analysis env | Technical debt findings by app/team/category; quality scores; dependency-derived analysis |
| **ODC Portfolio v2 / Dependency v1 / Asset v1** | ODC | **Supported** ([src](https://github.com/OutSystems/docs-odc/blob/main/src/eap/reference/apis/public-rest-apis/overview.md)) | OIDC/OAuth 2.0; API Client (client id+secret) from ODC Portal; Bearer token; granular per-stage asset perms | Deployed assets per environment; impact analysis + dependency data; asset info + revisions |
| **ODC MCP server** | ODC | Documented; GA status unstated ([src](https://success.outsystems.com/documentation/11/outsystems_mcp/outsystems_mcp_in_o11_and_odc/)) | ODC identity sign-in; OutSystems-hosted remote | Tenant-wide, full app lifecycle; confirmation gate before publish/deploy/rollback |
| **Service Center "Download Published Version"** | O11 | **Supported, UI only** ([src](https://success.outsystems.com/support/forge_components/forge_faqs/sharing_a_project/)) | Service Center session | The `.oml` file; no documented HTTP URL pattern |
| **OSSYS_* tables, officially named subset** | O11 | **Read-only by official instruction; schemas undocumented** ([src](https://success.outsystems.com/documentation/how_to_guides/data/data_migration_from_production_to_non_production_environment/outsystems_platform_metamodel/)) | DB credentials | App/module inventory, versions, full data model + physical↔logical names, static records, BPT definitions, tenants, settings, timers, SOAP in/out |
| **OSSYS_* tables, beyond the named subset** | O11 | **Undocumented; writes prohibited; rewrite on roadmap** ([src](https://www.outsystems.com/forums/discussion/95091/extended-metamodel-extendedmetamodel/)) | DB credentials | — |
| **Forge: Extended Metamodel 2.2.6** | O11 | **Not supported by OutSystems; uses private undocumented Platform APIs; may break on upgrade** ([src](https://www.outsystems.com/forge/component-overview/2146/extended-metamodel-o11)) | in-app | REST_Expose, REST_Web_Reference, App_Forge, other metamodel entities |
| **Forge: Discovery** | O11 | Forge component (community-governed) ([src](https://www.outsystems.com/forge/component-overview/1770/overview-o11)) | in-app | Factory architecture/dependency analysis; Application Layer Definitions; snapshot ingestible by Code Quality |
| **OML2XML extension** | O11 | Community, "early stage" ([src](https://www.outsystems.com/forums/discussion/96092/read-and-display-oml-file-as-text/)) | n/a | OML → inspectable XML |

### Recommended supported pipeline (inference)

1. **Inventory & topology** — LifeTime API v2 (O11) or ODC Portfolio v2 + Asset v1 (ODC). Pull `swagger.json` from the live LifeTime instance to get the exact contract.
2. **Factory dependency graph & quality** — Code Quality API (both platforms); optionally seed with a Discovery snapshot.
3. **Binary artifact acquisition** — LifeTime API v2 `.oap` operations (LT 11.22.0+), unpack to `.oml` modules. (`.oml` via Service Center is UI-only.)
4. **Per-module logic & structure** — Service Studio 11.55.91+ with the local MCP server on `127.0.0.1:41820`, driving GA read tools and ModelQL (`runQuery`, `Root { … }`). Investigate `getSerializedObject*` for bulk structural export.
5. **Data model physical mapping** — read-only queries against the officially-named OSSYS_ tables (`OSSYS_ENTITY`, `OSSYS_ENTITY_ATTR`, `OSSYS_ESPACE`, `OSSYS_ESPACE_ENTITY`, `OSSYS_DBCATALOG`), pairing entity keys with the eSpace `SS_Key`.

### Highest-value follow-ups

- Enumerate `C:\Program Files\OutSystems\Service Studio 11\Service Studio\` on a real install to resolve the `OutSystems.Model.Reader` / `OutSystems.Common` / `OutSystems.ObjectKeys` question, and read `outsystems11-mcp/servicestudio-mcp-oml/docs/` for the actual Model API namespace reference.
- Fetch the Code Quality API reference page and `code-quality-api-v1.md` for endpoints/auth/schemas.
- Fetch `portfolio-v2.md`, `dependency-v1.md`, `asset-v1.md` from `OutSystems/docs-odc` for ODC base paths and schemas.
- Research `.xif` / Integration Studio and Forge documentation generators (not covered in this pass).
- Identify the OSSYS_ table holding module-to-module reference edges.
