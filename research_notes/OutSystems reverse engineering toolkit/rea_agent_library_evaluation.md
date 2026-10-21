# Evaluation of github.com/morluto/rea ("REA: Reverse Engineer Anything") for an OutSystems reverse-engineering pipeline

> Verification note: all metadata below was read directly from the GitHub REST API and from
> `raw.githubusercontent.com` file contents on **2026-10-21**. Where a statement is my own
> reasoning rather than something I read in the repo, it appears under **Inferences**.

## Does https://github.com/morluto/rea exist and is it public?

### Takeaway
Yes — it exists, is public, MIT-licensed, and is one of the largest-by-stars repositories on GitHub (≈355k stars). It is **not** a "library of agents"; it is a single large TypeScript **MCP server + CLI** (npm package `rea-agents`) shipped alongside a small set of agent *skills*.

### Cited Findings
- `GET api.github.com/repos/morluto/rea` returns HTTP 200. `private: false`, `fork: false`, repo id `1209966933` — [GitHub API](https://api.github.com/repos/morluto/rea)
- Official description: "Reverse engineer anything with agents, from app behavior down to native binaries." Homepage `https://rea.tools` — [GitHub API](https://api.github.com/repos/morluto/rea)
- Metadata snapshot, 2026-10-21: **stars 354,982 · forks 89,162 · watchers/subscribers 1,257 · open issues+PRs 1,684 · repo size 93,350 KB · default branch `main`** — [GitHub API](https://api.github.com/repos/morluto/rea)
- `created_at: 2026-04-14T00:51:32Z`; `pushed_at: 2026-10-21T15:30:02Z` (**last commit the same day I checked**) — [GitHub API](https://api.github.com/repos/morluto/rea)
- Primary language TypeScript (33.2 MB), then JavaScript (3.0 MB), Python (761 KB), HTML (730 KB), Java (421 KB), C++ (110 KB), Swift (54 KB), Assembly (7 KB) — [languages API](https://api.github.com/repos/morluto/rea/languages)
- License: MIT (`spdx_id: MIT`), with a `THIRD_PARTY_NOTICES.md` dependency inventory — [GitHub API](https://api.github.com/repos/morluto/rea); [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Topics include `agent-skills`, `ai-agents`, `binary-analysis`, `claude-code`, `codex`, `decompiler`, `ghidra`, `hopper`, `mcp`, `model-context-protocol`, `reverse-engineering`, `static-analysis`, `touhou` — [GitHub API](https://api.github.com/repos/morluto/rea)
- Owner `morluto`: user account (not an org), id 76467478, 9,429 followers, 258 public repos, joined 2020-12-22, blog `https://x.com/morluto` — [user API](https://api.github.com/users/morluto)
- README carries an explicit anti-impersonation warning: "Get REA from morluto/rea, rea.tools, or the rea-agents npm package… A similar repository name or copied README does not establish that a download is official." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Secondary coverage confirms it hit GitHub Trending in Oct 2026 but reports **inconsistent numbers** (one aggregator claimed 234,477 stars / 58,512 forks as of 14 Oct; OSS Insight listed 7,355 forks) — [aitoolly](https://aitoolly.com/de/ai-news/article/2026-10-15-rea-emerges-on-github-trending-to-enable-ai-agents-to-reverse-engineer-software-and-native-binaries); [ossinsight](https://ossinsight.io/analyze/morluto/rea)

### Inferences
- The aggregator numbers are stale/unreliable; the API figures above are primary and should be the ones cited.
- A copycat/typosquat risk is real enough that the maintainer put a warning in the README — anyone installing should pin to the npm package `rea-agents` and the canonical repo URL.

### Gaps
- Could not independently audit the star count for inorganic growth (355k stars in ~6 months is extraordinary); GitHub's own counter is the only source.

## Stated purpose, architecture, and release history

### Takeaway
REA is "One MCP for reverse engineering across binaries, applications, and runtime behavior" — an evidence-oriented MCP tool server that an existing coding agent (Claude Code, Codex, Cursor, Gemini CLI, etc.) calls. It is conventional RE tooling *wrapped for agents*, not an LLM agent framework and not a collection of agent definitions.

### Cited Findings
- Stated purpose: "REA connects your agent to tools for inspecting native binaries, JavaScript and Electron apps, .NET assemblies, and websites… Analysis runs locally, and results include the evidence and limitations behind each conclusion." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Mechanism: "Your agent calls REA through MCP to inspect the target and trace relevant code. REA returns findings with their evidence… CLI commands use the same workflows." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- npm package `rea-agents`, version **6.7.0**, `type: module`, binaries `rea` / `rea-agents` → `scripts/rea.mjs` — [package.json](https://raw.githubusercontent.com/morluto/rea/main/package.json)
- 5 most recent GitHub releases: `rea-agents-6.7.0` (2026-10-18), `6.6.0` (2026-10-18), `6.5.0` (2026-10-14), `6.4.0` (2026-10-11), `6.3.0` (2026-10-09). Tag list goes back through `4.1.0` — [releases API](https://api.github.com/repos/morluto/rea/releases); [tags API](https://api.github.com/repos/morluto/rea/tags)
- README itself says "REA changes quickly, and new releases include frequent bug fixes. Keep your installation up to date." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Repo root contains `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `DISCLAIMER.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md`, plus `src/`, `tests/`, `bridge/`, `native/`, `docs/`, `website/`, `experiments/`, `third_party/` — [tree API](https://api.github.com/repos/morluto/rea/git/trees/main)
- `src/` has ~78 per-domain modules, each a backend: `src/ghidra`, `src/hopper`, `src/ida`, `src/jeb`, `src/kuna`, `src/cutter`, `src/rizin`, `src/objdump`, `src/gdb`, `src/frida`, `src/dotnet`, `src/android`, `src/apktool`, `src/adb`, `src/electron`, `src/javascript`, `src/browser`, `src/firmware`, `src/flutter`, `src/go`, `src/rust`, `src/il2cpp`, `src/gpu`, `src/evm`, `src/wasm`, `src/sqlite`, `src/pcap`, `src/captures`, `src/signals`, `src/process`, `src/model`, `src/windows` — [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1)
- MCP surface is registered through ~40+ `src/server/register*Tools.ts` files (`registerManagedTools.ts`, `registerNativeTools.ts`, `registerAndroidTools.ts`, `registerBrowserTools.ts`, `registerFirmwareTools.ts`, `registerEvmTools.ts`, `registerJavaScriptRecoveryTool.ts`, `registerInvestigationTools.ts`, …) — [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1)
- Runtime dependencies are deliberately narrow and version-pinned: `@modelcontextprotocol/client`/`server` 2.3.1, `@babel/parser` 8.0.4, `@electron/asar` 4.2.0, `playwright-core` 1.58.2, `isomorphic-git`, `evmole`, `plist`, `@zip.js/zip.js`, `zod` 4.4.3, `ajv`, `pino`, `ws`, `openpgp` — 43 prod deps, 25 dev deps — [package.json](https://raw.githubusercontent.com/morluto/rea/main/package.json)
- Build/quality tooling in root: `vitest` (4 configs), `stryker` mutation testing (2 configs), `oxlint`/`oxfmt`, `knip`, `jscpd`, `turbo`, `husky` — [tree API](https://api.github.com/repos/morluto/rea/git/trees/main)

### Inferences
- The architecture is a **provider-adapter pattern**: one MCP/CLI contract layer in front of many third-party RE engines, with an "Evidence" record type as the common output. REA supplies the orchestration and provenance, not the decompilation.
- Release cadence (6.3.0 → 6.7.0 in nine days) means any integration must pin a version; docs on `main` describe capabilities not yet in the released npm package (the README explicitly flags this with a "release availability" link).

## What agents/skills it actually defines

### Takeaway
There are only **five** skills in the repo, one of which is the user-facing investigation skill; the other four are internal maintainer skills. The "agents" in the name refers to the *agents that call REA*, not to a library of agent personas.

### Cited Findings
- Full contents of `.agents/skills/` — [tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1):
  - `reverse-engineer-anything/SKILL.md` (+ 6 reference docs: `android-applications.md`, `connection-and-recovery.md`, `evidence-workflows.md`, `javascript-applications.md`, `native-and-artifacts.md`, `runtime-observation.md`) — the user-facing investigation skill
  - `rea-analysis-optimization/SKILL.md` (+ `references/kuna-case-study.md`, `agents/openai.yaml`) — internal
  - `rea-ci-tests-audit/SKILL.md` (+ `references/measurement-and-ci.md`, `agents/openai.yaml`) — internal CI audit
  - `rea-changelog-update/SKILL.md` — internal
  - `rea-tool-design/SKILL.md` — internal
- The main skill's own frontmatter: `name: reverse-engineer-anything`, `metadata.version: "44"`, description = "Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA… **Skip REA for ordinary source-repository architecture analysis.**" — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- The skill's body reinforces the boundary: "Use REA when a claim depends on a shipped binary or package, decompilation, passive application runtime evidence, or comparison with behavior not established by available source. **For ordinary analysis of a complete source repository, use normal repository tools and do not run REA readiness or provider commands.**" — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- The skill is a routing table keyed on target type, naming concrete MCP tools: `analyze_javascript_application` (ASAR/Electron tree), `open_binary` + `inspect_artifact` (ZIP/APK/IPA/MSIX/DMG/PyInstaller), `open_bundle_resources` (Apple plist/IB/asset catalog), `inspect_android_package`, **`inspect_managed_artifact` (managed PE/CLI assembly)**, `inspect_firmware_regions` / `extract_firmware`, `list_browser_targets`, `capture_browser_scenario`, `inspect_web_network_capture` (HAR/SAZ/mitmproxy/qlog), `list_electron_targets`, `inspect_electron_fuses`, `inspect_packet_fields` / `inspect_packet_capture`, `inspect_signal_decoders` / `decode_signal_recording`, `inspect_wasm_artifact` — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- Skill section structure: "Connect only when needed", "Route the target first", "Work summary-first", "Plan broader investigations", "Read only the relevant guide", "Finish the task" — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- The .NET/managed surface is exactly **seven tools**: `inspect_managed_artifact`, `inspect_managed_members`, `inspect_managed_native_boundaries`, `compare_managed_members`, `verify_managed_native_boundaries`, `import_managed_reconstruction`, `project_managed_application_graph`; "Each has a matching CLI command: replace underscores with hyphens and prefix the name with `rea`" — [docs/managed-code-analysis.md](https://raw.githubusercontent.com/morluto/rea/main/docs/managed-code-analysis.md)
- Managed analysis is strictly static: "REA inspects .NET PE/CLI artifacts **without loading or executing their code**… It can identify an assembly, inspect metadata and CIL, compare members across builds, and connect declared native calls to supplied native-analysis evidence." Collections pageable per assembly: `types`, `exported_types`, `fields`, `methods`, `member_refs`, `call_edges`, `field_accesses`, `user_strings` — [docs/managed-code-analysis.md](https://raw.githubusercontent.com/morluto/rea/main/docs/managed-code-analysis.md)
- Managed scope limits stated outright: "it does not unpack .NET single-file hosts or infer a NativeAOT identity from an ordinary native PE. It does not decode IL2CPP… Inputs without admitted CLI metadata do not become managed assemblies through naming or routing guesses." — [docs/managed-code-analysis.md](https://raw.githubusercontent.com/morluto/rea/main/docs/managed-code-analysis.md)
- 74 top-level docs in `docs/`, including `reconstruction-coverage.md`, `reconstruction-obligation-ledgers.md`, `reconstruction-readiness.md`, `javascript-recovery.md`, `javascript-application-graph.md`, `native-function-matching.md`, `mcp-contracts.md`, `mcp-prompts.md`, `roadmap.md`, `testing.md`, `tool-design.md` — [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1)
- `docs/mcp-contracts.md` (1,156 lines) defines the contract layer: Tool results, Untrusted target content, Retained application Evidence inputs, Identity and discovery, Transports, Progress and cancellation, Request scope and local effects, Integrity record-and-continue, Schema advertisement, Output schemas — [mcp-contracts.md](https://raw.githubusercontent.com/morluto/rea/main/docs/mcp-contracts.md)
- The canonical tool catalog is **build-generated, not checked in**: "Run `npm run docs:generate` in a source checkout to generate the machine-readable catalog at `docs/public/product-catalog.json`… These outputs describe the exact source revision being built; they are not checked-in snapshots." — [mcp-contracts.md](https://raw.githubusercontent.com/morluto/rea/main/docs/mcp-contracts.md)

### Inferences
- Counting the register-tool modules and the per-domain docs, the live tool count is plausibly in the low hundreds, but I could not produce an exact number (see Gaps).
- The "Evidence" abstraction — every result carrying its provenance, coverage, unknowns and limitations, with paged retained views keyed by `evidence_id` and artifact SHA-256 — is the most transferable design idea in the repo for an OutSystems pipeline, independent of whether REA itself is used.

### Gaps
- Exact MCP tool count is unverifiable without cloning and running `npm run docs:generate`; `https://rea.tools/rea/product-catalog.json` and `https://rea.tools/product-catalog.json` both returned HTTP 404.

## Inputs, outputs, dependencies, prerequisites

### Takeaway
Inputs are **shipped artifacts and runtime observations** (binaries, packages, assemblies, JS bundles, APKs, captures, live browser/Electron targets) — never source trees or model files. Output is structured evidence (pseudocode, CIL, graphs, inventories) that the *calling agent* turns into explanation or code. No REA-issued API key; the LLM is whatever agent you already run.

### Cited Findings
- Install: `npx rea-agents setup` → "Setup adds REA's MCP server and matching workflow instructions, with backups of existing configuration. Restart your agent afterward." Supported clients per the skill: `claude_code`, `claude_desktop`, `codex`, `cursor`, `gemini_cli`, `windsurf`, `devin`, `opencode`, `antigravity`, `copilot_cli`, `commandcode`, `vscode`, `grok_build`, `omp`, `grok_bot` — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md); [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- Runtime requirement: "REA requires Node.js 22.x (>=22.19), 24.x (>=24.11), or 26+, plus npm." `engines: { node: "^22.19.0 || ^24.11.0 || >=26.0.0" }` — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md); [package.json](https://raw.githubusercontent.com/morluto/rea/main/package.json)
- Bring-your-own engines per target: Hopper/Ghidra/IDA for native decompilation; JADX + full JDK for APKs; Binwalk/Unblob (Linux) for firmware; pwntools (Linux x64) for ELF layout and crash dumps; WABT 1.0.42 for WASM; TShark/capinfos 4.x + prlimit for pcap; sigrok-cli 0.7.2 for logic traces; adb for devices; Apktool for Android resources; a caller-started JEB MCP client via `REA_JEB_MCP_URL`; a Chrome-family browser for website work — [README target table](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- "Static JavaScript and .NET inspection read the supplied files **without running** the application. Runtime capture runs or interacts with the selected target using **your user permissions**; each runtime guide describes its effects." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- "REA setup never installs or upgrades Node.js, npm, Homebrew, Java, Ghidra, IDA, JADX, Kuna, Binwalk, or Unblob." — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- No cloud dependency: "REA analyzes targets locally. Your agent receives the tool results, and its model provider has its own data policy." — [README FAQ](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Works CLI-only without MCP: `npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json` — "No MCP registration or native engine is required." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md); [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- Linux caveat: Ghidra, JADX, firmware launches and static JS/Electron analysis "require a procps-compatible `ps` on REA's `PATH` for process ownership checks." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)

### Inferences
- Zero-marginal-cost evaluation is possible: the `.NET` and JavaScript paths need only Node 22+ and no commercial decompiler, which is exactly the subset relevant to OutSystems. A trial can be done with two `npx` commands against a deployed OutSystems DLL and a front-end bundle.

## Fitness for an OutSystems reverse-engineering pipeline

### Takeaway
REA is oriented at the **"no source, only a shipped artifact"** end of the problem. It will not read `.oml`/`.oap` files and has zero low-code awareness, so it is useless for the unpack-and-recover-model stage and for spec generation. It is, however, a credible fit for the *deployed-artifact* flank of an OutSystems investigation: static .NET/CIL inspection of compiled eSpace assemblies, front-end JS bundle module graphs, and HAR capture analysis of the app's own API traffic.

### Cited Findings
- **No OutSystems or low-code support exists in the repo.** I searched all 5,076 blob paths in the `main` tree: `outsystems` → 0 hits; `mendix` → 0; `lowcode`/`low-code` → 0; `powerapps` → 0; `salesforce` → 0. The 4 `oml` hits are coincidental substrings (`GhidraDosComLoadImage.test.ts`, two `tomlConfiguration*` tests, `website/wrangler.toml`); the 2 `espace` hits are the substring in "namespace" — [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1)
- The README target table covers 28 target classes; **none** is a model file, metadata repository, or low-code package — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Relevant capability #1 — managed/.NET, static, no commercial tool needed: metadata, CIL instruction bodies, `call_edges`, `field_accesses`, `user_strings` literal pool, `member_refs`, cross-build `compare_managed_members`, and `project_managed_application_graph` to fold managed findings into an application graph — [docs/managed-code-analysis.md](https://raw.githubusercontent.com/morluto/rea/main/docs/managed-code-analysis.md)
- Relevant capability #2 — JavaScript/Electron: returns "Modules, imports, source maps, routes, IPC and native add-on relationships"; see also `docs/javascript-recovery.md` and `docs/javascript-application-graph.md` — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md); [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1)
- Relevant capability #3 — websites and traffic: "Page structure, scripts, network observations and requested screenshots" (needs a Chrome-family browser); saved HAR/SAZ captures give "Requests, responses, exposed payloads and source locations" — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Relevant capability #4 — SQLite: "Tables, columns, indexes, views, triggers and selected ordinary-table rows" (Node 24.15+/26+) — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- Relevant capability #5 — a reconstruction-discipline doc set already exists: `docs/reconstruction-readiness.md`, `docs/reconstruction-coverage.md`, `docs/reconstruction-obligation-ledgers.md`, and the managed tool `import_managed_reconstruction` ("Import decompiled code against verified static member identities") — [docs/managed-code-analysis.md](https://raw.githubusercontent.com/morluto/rea/main/docs/managed-code-analysis.md); [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1)
- **Explicit anti-fit signal**: the skill description instructs agents to "Skip REA for ordinary source-repository architecture analysis", and the body repeats "For ordinary analysis of a complete source repository, use normal repository tools and do not run REA readiness or provider commands." — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- Showcase evidence of what REA is actually good at: DX-Ball sound-pan reconstruction ("passes 3,205 original-x86 cases and reproduces all 63 compiled function bytes"), Notion Electron clipboard IPC trace, TH04 16-bit DOS bullet-ring recovery — [README showcases](https://raw.githubusercontent.com/morluto/rea/main/README.md); [rea.tools/showcase](https://rea.tools/showcase/)

### Inferences
- **Pipeline stage mapping** (stage names from the assignment):
  1. *Unpack `.oml`/`.oap`* — **no fit, 0%.** REA will refuse the input by design ("Inputs without admitted CLI metadata do not become managed assemblies through naming or routing guesses"). Needs purpose-built tooling: OutSystems' own `OSPTool`/Service Studio APIs, or an independent `.oml` container parser. New work, not REA work.
  2. *Recover model* — **no fit** for the model-file route. There is a **partial alternative route**: if the OutSystems app is deployed, the server-side logic exists as compiled .NET assemblies and the front end as JS bundles, both of which REA reads today. This is a *different* and lossier source of truth than the `.oml` model (it recovers generated code, not the visual model), but it is independent corroboration and it works when you only have a running environment and no `.oml`.
  3. *Generate spec* — **weak fit.** REA produces evidence records, not specifications. Nothing in the repo generates requirements, business rules, or user stories; the agent calling REA does that ad hoc. This is where Reversa-style agents belong (below).
  4. *Generate target code* — **weak/indirect fit.** The `import_managed_reconstruction` + reconstruction-ledger machinery is a genuinely useful *verification* pattern (does the rewritten member match the verified original identity?), but it is built around CIL/native members, not OutSystems screens, entities, or server actions.
- **Where new agents would be needed** if REA were adopted: an `.oml`/`.oap` unpacker tool in REA's provider style; an OutSystems model-graph projector analogous to `project_managed_application_graph`; an eSpace-aware mapper that links generated .NET types back to OutSystems artifacts (screens, server actions, entities); and spec-synthesis agents that REA deliberately does not provide.
- Caveat on my own reasoning: that OutSystems traditional/reactive server-side logic compiles to .NET assemblies and the reactive front end ships as JS bundles is **background knowledge, not something I verified in the REA repo** — the repo has no OutSystems content at all. The feasibility of the "deployed-artifact flank" should be confirmed empirically by running `rea inspect-managed-artifact` against a real OutSystems-generated DLL before any plan depends on it.
- Net recommendation shape: treat REA as an **optional corroboration/forensics lane** for deployed OutSystems artifacts and as a **design reference** for evidence provenance; do not architect the main `.oml` → spec → code pipeline on it.

### Gaps
- No public report, issue, or case study of anyone pointing REA at an OutSystems artifact. I found none, so the `.NET`-assembly route remains untested in this specific context.

## Comparable alternatives for agentic RE / spec recovery

### Takeaway
For the stage that actually matters to an OutSystems pipeline — spec recovery from a code/model representation — **sandeco/reversa** is the far better match and is genuinely "a library of agents". The GhidraMCP/IDA-MCP family are better-established but solve the same binary-first problem REA does.

### Cited Findings
- **sandeco/reversa** — "Transform legacy systems into executable specifications for AI coding agents". **1,783 stars · 443 forks · 23 open issues · JavaScript · MIT · created 2026-04-26 · last push 2026-10-21** — [GitHub API](https://api.github.com/repos/sandeco/reversa)
  - Positioning: "Reversa is a specification reverse-engineering framework. Install it inside a legacy project and it coordinates a team of specialized AI agents to analyze the existing code and generate complete, traceable specifications ready for use by any coding agent." — [README](https://raw.githubusercontent.com/sandeco/reversa/main/README.md)
  - Backed by a paper: "Reversa: A Reverse Documentation Engineering Framework for Converting Legacy Software into Operational Specifications for AI Agents", Macedo & da Costa, May 2026 — [arXiv 2605.18684](https://arxiv.org/abs/2605.18684)
  - Architecture is literally an agent library: it installs into `.agents/skills/` (and `.claude/skills/` for Claude Code), organizes agents into **eleven specialized Teams** (Reversa Agents Core/Discovery, Ideation, Code New Project, Code Forward, Migration, Pricing and Size, Bug, Code Quality, Translators, …), and exposes orchestrators `/reversa` (5-phase Discovery pipeline), `/reversa-forward`, `/reversa-migrate`, `/reversa-docs`, `/reversa-new`, `/reversa-brainstorm`, `/reversa-debugger`, `/reversa-refactor`, `/reversa-autonomous`. Independent agents: Visor, Data Master, Design System, Soul Extractor, Reconstructor — [README](https://raw.githubusercontent.com/sandeco/reversa/main/README.md)
  - Safety posture: installer "only creates new files… and never modifies or deletes any existing file"; agent writes restricted to `.reversa/` and `_reversa_sdd/`; "Reversa does not request, store, or transmit API keys from any LLM service." Orchestrators pause for `CONTINUAR` between agents — [README](https://raw.githubusercontent.com/sandeco/reversa/main/README.md)
- **mrexodia/ida-pro-mcp** — "AI-powered reverse engineering assistant that bridges IDA Pro with language models through MCP". **13,069 stars · 1,573 forks · 56 open issues · Python · MIT · created 2025-03-25 · last push 2026-09-26** — [GitHub API](https://api.github.com/repos/mrexodia/ida-pro-mcp)
- **LaurieWired/GhidraMCP** — "MCP Server for Ghidra". **11,453 stars · 1,205 forks · 94 open issues · Java · Apache-2.0 · created 2025-03-23 · last push 2026-10-10** — [GitHub API](https://api.github.com/repos/LaurieWired/GhidraMCP)
- **cyberkaida/reverse-engineering-assistant** (ReVa) — "MCP server for reverse engineering tasks in Ghidra". **879 stars · 80 forks · 15 open issues · Java · Apache-2.0 · created 2023-08-18 · last push 2026-10-20** — [GitHub API](https://api.github.com/repos/cyberkaida/reverse-engineering-assistant)
- **mahaloz/DAILA** — "A decompiler-agnostic plugin for interacting with AI in your decompiler". **711 stars · 60 forks · 8 open issues · Python · BSD-2-Clause · created 2022-12-05 · last push 2026-07-14** — [GitHub API](https://api.github.com/repos/mahaloz/DAILA)

### Inferences
- The right combination for an OutSystems pipeline is likely **Reversa (or a Reversa-style agent team) for spec recovery and migration planning**, with **REA as an optional evidence lane** when only deployed artifacts exist. They are complementary, not competing: REA explicitly declines source-repository analysis, which is precisely Reversa's domain.
- Reversa is itself young (created April 2026) and far smaller; its `/reversa-migrate` ("Turn legacy specs into a rebuild plan for a modern stack") maps onto the OutSystems → target-code stage, but it assumes a readable source tree, so an `.oml` → readable-representation step is still prerequisite work either way.

### Gaps
- Reversa's README mentions no OutSystems/low-code support either; I did not find any low-code-specific agentic spec-recovery project. I searched only once for alternatives, so the landscape sweep is not exhaustive.
- I did not verify Reversa's agent prompt quality by reading its skill files (only its README and GitHub metadata).

## Red flags and risks

### Takeaway
Maintenance, licensing and test discipline are all strong — unusually so. The real risks are operational: extreme release churn, a large unaudited local-execution surface, legal/authorization exposure, and a recency/popularity profile that invites typosquatting.

### Cited Findings
- **Not unmaintained.** Last commit 2026-10-21 15:28 UTC, the same day as this check; 8 merges in the preceding ~35 minutes. **1,848 merged PRs** and **1,646 closed issues** in ~6 months — [commits API](https://api.github.com/repos/morluto/rea/commits); [search API: closed issues](https://api.github.com/search/issues?q=repo:morluto/rea+is:issue+is:closed); [search API: merged PRs](https://api.github.com/search/issues?q=repo:morluto/rea+is:pr+is:merged)
- **Not untested.** **1,925 `*.test.ts` files**; 1,575 files under `tests/` across `acceptance`, `boundary`, `composition`, `conformance`, `evaluation`, `fixtures`, `process-global`, `support`; 2,480 files under `src/`. Mutation testing configured via two Stryker configs; four Vitest configs incl. dedicated `vitest.reverse-tools-semantics.config.ts` — [recursive tree API](https://api.github.com/repos/morluto/rea/git/trees/main?recursive=1); [tree API](https://api.github.com/repos/morluto/rea/git/trees/main)
- **Licensed.** MIT, with `THIRD_PARTY_NOTICES.md`, a `licenses/` directory, and a `SECURITY.md` for vulnerability reporting — [GitHub API](https://api.github.com/repos/morluto/rea); [tree API](https://api.github.com/repos/morluto/rea/git/trees/main)
- **Single-maintainer concentration.** Contributions: `morluto` 2,104, `N0zoM1z0` 592, `kaoru0822-kitauji` 524, `rudycelekli` 91, `gensokyo-dev` 54, `github-actions[bot]` 44, then a long tail of ≤14 — [contributors API](https://api.github.com/repos/morluto/rea/contributors)
- **Open issue backlog 1,684** (issues + PRs). The newest open issues are maintainer-style precision bug reports, e.g. "#6068 [Bug] Managed source changes return Evidence integrity errors and incorrect recovery", "#6067 [Bug] PyInstaller extraction reports changed source admission as unreadable I/O", "#6072 [Bug] Frida CLI omits typed cancellation during final provider cleanup" — [issues API](https://api.github.com/repos/morluto/rea/issues?state=open)
- **Runtime execution risk, stated by the project**: "Runtime capture runs or interacts with the selected target using your user permissions"; the MCP contract has dedicated sections on "Untrusted target content" and "Request scope and local effects" — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md); [mcp-contracts.md](https://raw.githubusercontent.com/morluto/rea/main/docs/mcp-contracts.md)
- **Setup mutates agent configuration**: it writes MCP registrations and replaces the bundled skill; mitigations are backups, `--dry-run --json` plan review, and explicit `--yes` / `--install-hopper` approval — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md); [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- **Legal posture**: "REA is for lawful research, education, interoperability, software preservation, and analysis of software you own or are authorized to examine"; `DISCLAIMER.md` holds responsible-use guidance; commercial tool licenses (IDA/Hex-Rays, Hopper, JEB) must be legally obtained — "REA grants no tool license, key, or activation entitlement. Cracked copies, stolen keys, unauthorized key sharing, and bypassing license restrictions are not authorized." — [README](https://raw.githubusercontent.com/morluto/rea/main/README.md)
- **Docs-vs-release drift, acknowledged**: "a skill installed from repository main may describe capabilities absent from an older npm release" — [SKILL.md](https://raw.githubusercontent.com/morluto/rea/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- **Claims are hedged, not oversold.** Secondary coverage warns against the claim that REA "rebuilds original source code"; the repo's own FAQ says only "Native analysis returns pseudocode and assembly… Your agent uses these findings to write and test an implementation." — [pasqualepillitteri (FR)](https://pasqualepillitteri.it/fr/news/23846/rea-reverse-engineer-anything-github-vrai-faux); [README FAQ](https://raw.githubusercontent.com/morluto/rea/main/README.md)

### Inferences
- The notable disconnect is between the repo's *engineering* maturity (very high: contract docs, mutation testing, evidence provenance, explicit limitation reporting) and its *age* (6 months). Nothing I read is unsupported by code I could see, but 93 MB / 5,076 files is far beyond what can be audited in a review of this scope.
- For an enterprise OutSystems engagement, the authorization question is the binding constraint, not the tooling: decompiling a customer's deployed OutSystems assemblies may breach OutSystems licensing or the customer's own contracts. That is a legal gate to clear before any technical trial.
- Practical risk controls if trialled: pin `rea-agents@6.7.0` rather than `@latest`; use the CLI (`--json`) rather than registering the MCP server, to avoid mutating agent config; run only the static paths (`inspect-managed-artifact`, `analyze-javascript-application`) which neither execute the target nor need a commercial decompiler; keep targets in an isolated directory.

### Gaps
- `SECURITY.md`, `DISCLAIMER.md`, `AGENTS.md` and `CONTRIBUTING.md` were confirmed to exist but not read in full.
- No third-party security audit, CVE history, or supply-chain review of `rea-agents` was found.
- `docs/roadmap.md` exists but was not read, so planned capabilities (which might include low-code or additional managed support) are unknown.
