# OML/OAP File Format Internals and Unpacking Techniques

> **Evidence note.** A large part of this document is **(a) first-party verified**: I reverse-engineered a real
> OutSystems 11 application package present in this repository —
> `/Users/I5285/Documents/GitHub/Outsystem-ReverseEngineering/Test Application.oap`
> (3,096,013 bytes, created 2026-10-21, HubServerVersion `11.42.1.47790`) — and parsed it byte-for-byte to a
> complete, exact, self-checking structural model (93/93 fragments decoded, byte totals matching to the byte).
> Those findings are marked **[VERIFIED LOCALLY]** and are reproducible with the commands given.
> Findings from the web are marked **[DOCUMENTED]** (official OutSystems), **[COMMUNITY]** (forum/GitHub), or
> **[SPECULATION]**. Nothing is presented as fact without a source or a reproducible command.

---

## Q1: What is the container structure of a .oap file? What about .osp and .oar?

### Takeaway

A `.oap` is a plain ZIP (deflate) archive containing exactly one `Manifest.xml` (the "Solution Pack Manifest")
plus one directory per application holding the `.oml` module files. `.osp` is the same container shape but
describes a multi-application *solution* rather than a single application. **I found no evidence that `.oar` is an
OutSystems format at all** — it appears to be a false premise in the research brief.

### Cited Findings

**`.oap` container — [VERIFIED LOCALLY]**

`file` and `unzip -l` on the real O11 package:

```bash
$ file "Test Application.oap"
Test Application.oap: Zip archive data, at least v2.0 to extract, compression method=deflate

$ unzip -l "Test Application.oap"
  Length      Date    Time    Name
---------  ---------- -----   ----
   186445  10-21-2026 11:18   Manifest.xml
     (zip comment: "The Solution Pack Manifest")
        0  10-21-2026 11:18   Test_Application/
  3053090  10-21-2026 11:16   Test_Application/TestApplication.oml
```

- First 4 bytes are `50 4b 03 04` (`PK\x03\x04`) — standard local file header, no OutSystems wrapper, no ZIP password. Extraction needs no key. **[VERIFIED LOCALLY]**
- The ZIP **archive comment is the literal string `The Solution Pack Manifest`** — a useful magic/fingerprint for identifying OutSystems packs. **[VERIFIED LOCALLY]**
- Layout is `Manifest.xml` at the root + one folder per application named after the application's *solution* name (`Test_Application/`), containing the module `.oml` files. **[VERIFIED LOCALLY]**

**`Manifest.xml` schema — [VERIFIED LOCALLY]**

Root element is `<Pack>`, containing `<Solutions>` → `<Solution>` → `<References>` and `<Applications>`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Pack Schema="3" HubServerVersion="11.42.1.47790" LastUpgradeVersion="11.0.0.200"
      IsApplicationPack="true" UID="+5oc2juJUkaapQxfdR6pmw" Creation="2026-10-21 11:18:18">
  <Solutions>
    <Solution Schema="3" HubServerVersion="11.42.1.47790" UID="JDeiRWI8dUqsENq57vN8yg"
              Creation="2026-10-21 11:18:17" Name="Test_Application"
              Description="An application to " ActivationCode="" IsTransient="true">
      <References>
        <Reference UID="Am0mHuuAS0yPh37L4weNBQ" Kind="eSpace" Name="TestApplication" ...>
          <LogicalDatabases /><DBCatalog LogicalName="" />
        </Reference>
      </References>
      <Applications>
        <Application UID="JDeiRWI8dUqsENq57vN8yg" Name="Test Application"
          FrontOfficeEspaceKey="Am0mHuuAS0yPh37L4weNBQ" FrontOfficeEspaceName="TestApplication"
          BackOfficeEspaceName="" TemplateKey="Wrm0V2ZyskqM7KobRok75w" PrimaryColor="#FFB61E"
          APIHash="591279d1-98c0-d3da-cb17-78c37ebe9f64"
          ContentHash="725d1ea1-5093-8ec0-78bb-ddbefd60015a"
          OriginEnvironmentCode="BY0.N5U.BAT.OHU.EZF.OZS.KPW.AUT"
          ForgeBaseVersion="0.0" OutdatedReferences="false" ApplicationKind="CrossDevice">
          <Icon>iVBORw0KGgoAAAANSUhEUgAA...</Icon>   <!-- base64 PNG -->
```

Notable, directly exploitable attributes **[VERIFIED LOCALLY]**:
- `IsApplicationPack="true"` — this is the discriminator between a `.oap` (application pack) and a `.osp` (solution pack); a `.osp` is expected to carry `IsApplicationPack="false"` and multiple `<Application>`/`<Reference>` entries. (The `false` value itself is **[SPECULATION]** by symmetry — I only had a `.oap` to test.)
- `Kind="eSpace"` on `<Reference>` — module kind. OutSystems internally calls modules *eSpaces*; extensions appear as a different `Kind`.
- `ApplicationKind="CrossDevice"`, `PrimaryColor`, `TemplateKey` — app metadata.
- `APIHash` / `ContentHash` / `OriginEnvironmentCode` — integrity + provenance values.
- `<Icon>` holds the app icon as **base64 PNG, inline** — directly extractable with no OutSystems tooling.
- `Manifest.xml` was 186 KB for a trivial one-module app, because the manifest also carries the full reference closure.

**`.osp` (Solution Pack) — [COMMUNITY] + [DOCUMENTED]**
- "Basically a zipfile, with all the modules that are part of a solution, so you can rename it to .zip" to inspect it — [OutSystems forum: difference between OAP, OSP & OML](https://www.outsystems.com/forums/discussion/71018/can-some-explain-me-what-is-the-difference-between-oap-osp-oml-file/)
- A `.osp` is "a solution of different modules/extensions (possibly from different applications)", whereas a `.oap` "contains all the modules/extensions in an application" — [OutSystems forum](https://www.outsystems.com/forums/discussion/71018/can-some-explain-me-what-is-the-difference-between-oap-osp-oml-file/); see also [.oap vs .oml](https://www.outsystems.com/forums/discussion/57168/what-is-the-difference-between-oap-and-oml-file/) and [.oml vs .oap for a module](https://www.outsystems.com/forums/discussion/58038/what-is-the-exact-difference-between-oml-and-oap-file-for-an-module/)
- Officially, the **Solution Pack Tool (`osptool.exe`)** "publishes OutSystems solutions on an environment" and its command line **accepts either an `.osp` or an `.oap` file** — [OutSystems 10 docs: Solution Pack Tool command line reference for Java](https://success.outsystems.com/documentation/10/setting_up_outsystems/unattended_installation_and_upgrade/unattended_installation_and_upgrade_for_java/solution_pack_tool_command_line_reference_for_java/). This is the strongest *official* evidence that `.oap` and `.osp` share one container format — one tool consumes both.
- `osptool.exe` is the registered handler for `.osp` — [PC Matic file extension library](https://www.pcmatic.com/company/libraries/fileextension/application.asp?appname=osptool.exe.html)
- Forge upload format guidance: the recommended Forge format is the Application Package (`.oap`), max upload 256 MB — [OutSystems Support: Sharing a project](https://success.outsystems.com/support/forge_components/forge_faqs/sharing_a_project/)

**`.oar`**
- I searched specifically for a `.oar` OutSystems extension and **found no source describing it**. See the [search-surfaced extension listings](https://www.filesuffix.com/en/extension/oap) which tie `.oap` to `.oml` and `.osp` only. Treat `.oar` as **not an OutSystems format** unless the user can cite where they saw it.

### Inferences

- Because the ZIP has no password and no custom wrapper, *the entire `.oap` layer is fully open*: manifest metadata, app icons, module inventory, reference graph and version stamps are recoverable with nothing but `unzip`. The only hard part is the `.oml` payload inside.
- `Schema="3"` on both `<Pack>` and `<Solution>` is a versioned manifest schema; a parser should branch on it.

### Gaps

- I did not have a `.osp` or a multi-module `.oap` to verify the multi-application layout empirically; the single-app layout is verified, the multi-app shape is inferred from the community description.
- No official OutSystems page documents the `Manifest.xml` schema. The canonical O11 "deploy using solutions" doc URL I tried returned HTTP 404, so the manifest schema remains undocumented officially.

---

## Q2: What is the internal structure of an .oml file? Magic bytes, compression, encryption?

### Takeaway

**Fully solved and verified.** An `.oml` is a proprietary binary container: ASCII magic `OML`, a little-endian
uint32 header length, a pipe-delimited plaintext ASCII header, then a **raw DEFLATE** stream (no zlib/gzip
wrapper) whose inflated contents are a fragment directory followed by N concatenated **Fast Infoset**
(ITU-T X.891 / ISO/IEC 24824-1 binary XML) documents. **It is not encrypted.**

### Cited Findings — [ALL VERIFIED LOCALLY]

**Magic bytes and header**

```
$ xxd TestApplication.oml | head -8
00000000: 4f4d 4c7b 8d00 0031 312e 302e 3431 352e  OML{...11.0.415.
00000010: 3130 307c 3131 2e35 352e 3933 2e36 3533  100|11.55.93.653
00000020: 3333 7c31 3535 7c41 6d30 6d48 7575 4153  33|155|Am0mHuuAS
00000030: 3079 5068 3337 4c34 7765 4e42 517c 5277  0yPh37L4weNBQ|Rw
```

Byte-exact layout:

| Offset | Size | Content |
|---|---|---|
| `0x00` | 3 | ASCII magic **`OML`** = `4F 4D 4C` |
| `0x03` | 4 | uint32 **little-endian** header length. Here `7b 8d 00 00` = `0x8D7B` = **36,219** |
| `0x07` | 36,219 | **Plaintext ASCII header**, `|`-delimited fields |
| `0x07 + hdrLen` = 36,226 | rest | **Raw DEFLATE** stream (3,016,864 bytes), inflating to 8,185,876 bytes |

Verified by: `printable run from offset 7 length 36219` — the printable ASCII run is *exactly* the declared
header length, so the uint32 at `0x03` is unambiguously the header length.

**Header fields (pipe-delimited), in order, as observed:**

```
11.0.415.100                      # OML / model format version
| 11.55.93.65333                  # producing platform (Service Studio) version
| 155                             # schema or model revision number
| Am0mHuuAS0yPh37L4weNBQ          # eSpace (module) UID — matches Manifest.xml Reference UID
| RwMjGVcwcGSBdSaklTLyzA          # second UID (key)
| True                            # boolean flag
| TestApplication                 # module Name
| An application to               # module Description
| 2026-10-21 11:16:15             # LastModified timestamp
| J7pB0r6rRF5GhEoPIwOswg          # UID
| /NRWebFlows.fWtJs57lI0qCTlwkcDoxDA/NodesShownInESpaceTree.+Sc1+XsmWUiszZQMKnQqBw
| eyIkaWQiOiIxIiwiJHR5cGUiOiJTZXJ2aWNlU3R1ZGlvLlByZXNlbnRlci5BZ2dyZWdhdG9yUHJlc2VudGVyK1N0YXRlLCAu...
```

The last field is **base64**; decoding it yields **Newtonsoft.Json-style JSON with `$id`/`$type`/`$ref`
reference-tracking** — i.e. serialized Service Studio *UI* state, not the model:

```json
{"$id":"1","$type":"ServiceStudio.Presenter.AggregatorPresenter+State, ServiceStudio.Presenter",
 "presenterId":"Window 1+0","isFocused":false,"childPresentersState":[
  {"$id":"3","$type":"ServiceStudio.Presenter.AbstractObjectTreeEditorPresenter+State, ServiceStudio.Presenter",
   "selectedFolders":[],"expandedNodes":[{"$type":"...+State+ExpandedNode, ServiceStudio.Presenter",
   "ObjectId":{"$type":"ServiceStudio.WeakReferences.AbstractObjectIdentifier, ServiceStudio.Framework",
   "ownerESpaceInstanceId":"a584d8ad-1273-41a7-ace9-46990e067c6a",
   "compoundKey":{"$type":"OutSystems.MetaModel.CompoundKeys.RootCompoundKey, OutSystems.MetaModel"}}...
```

This leaks real internal assembly and namespace names: `ServiceStudio.Presenter`, `ServiceStudio.Framework`,
**`OutSystems.MetaModel`**, `OutSystems.MetaModel.CompoundKeys.RootCompoundKey`.

**Compression: raw DEFLATE, confirmed**

```python
import struct, zlib
d = open('TestApplication.oml','rb').read()
assert d[:3] == b'OML'
p = 7 + struct.unpack('<I', d[3:7])[0]        # 36226
inflated = zlib.decompressobj(-15).decompress(d[p:])   # wbits=-15 => RAW deflate
# -> 8,185,876 bytes, unused_data == b'' (stream consumed exactly)
```

- `wbits=-15` (raw) succeeds; there is **no zlib header** (`78 9C`/`78 DA`/`78 01`) and **no gzip header** at the payload start. The payload begins `ec bd 09 98 e3 58 75 2f`, a typical raw-deflate first byte pattern.
- The stream is consumed **exactly** (`unused_data` empty) — the whole post-header remainder is one deflate stream.
- This matches the embedded `ICSharpCode.SharpZipLib` dependency in the community tool (see Q3).
- Note: `78 9c` / `78 da` / `78 01` byte pairs *do* occur at many offsets inside the compressed blob — these are coincidental, not nested zlib streams. Do not use them as framing hints.

**Encryption: none**

- Entropy of the inflated blob is **6.37 bits/byte** over the first 200 KB — well below the ~7.99 expected for ciphertext or compressed-again data.
- The inflated blob contains **112,668 printable-ASCII runs of ≥12 chars**, including real model identifiers (`Widgets#DWl6nx5eD0Ws5ElP75cfgQ`, `UserActions#iCnZkeZp7US8oQ7YQB15yg`, `CompilationUnits`, `SoftwareUnits`, `VerifyCaches`).
- Conclusion: **no encryption anywhere in the `.oml` pipeline.** The format is protected by *obscurity and binary-XML encoding only*.

**Inflated layout: fragment directory + concatenated Fast Infoset documents**

The inflated blob is structured as:

| Region | Content |
|---|---|
| `0x0000` – `0x05D3` (0–1491) | Preamble. Starts `5d 00 00 00` (uint32 = 93) followed by 93 bytes of high-entropy data, then further opaque bytes. **Purpose not determined** (see Gaps). |
| `1492` – `5523` | **Fragment directory**: 93 entries, each `[uint32 LE nameLen][name ASCII][uint32 LE contentLen]` |
| `5524` – `8185875` | **93 fragment bodies, concatenated in directory order**, each a complete Fast Infoset document |

Self-consistency proof — this is why I consider the structure *solved* rather than guessed:

```
DIRECTORY start=1492  entries=93  dir_ends=5524
sum(lengths)=8180352  content_space=8180352  match=True
contents: FastInfoset=93/93   non-FI first4 counts={}
end cursor 8185876  file len 8185876  exact match True
```

Every one of the 93 declared lengths is consumed, every body starts with the Fast Infoset magic, and the cursor
lands exactly on EOF. There is no slack, so the framing is correct.

**Fast Infoset confirmation**

- All 93 bodies begin with `E0 00 00 01` — the Fast Infoset document magic/identification per ITU-T X.891 ([Fast Infoset, Wikipedia](https://en.wikipedia.org/wiki/Fast_Infoset): ASN.1-based, tag/length/value blocks, compression done as part of XML generation).
- The first body decodes recognizably even to a naive strings pass:
  ```
  e0 00 00 01 00 |\r eSpaceFragment x \x04 Count @2 \xf0| @\x01
  NRWebWidgets.CustomWidget-OutSystems.Plugin.NRWidgets.AdvancedHtml
  x\x02 Key H \r ytdb+CTWAUS0m+QJST427A
  x\x12 CustomObjectImplKey H \r fD0nWzzBDWruDF+6ix3Xnw
  x\x04 Width H \x04 (fill parent)
  \xf0< \x0c TextResources  \xf0< \x07 Metadata  \xf0< \x06 Visible
  < \x0f ParsedExpression | \x06 Boolean  x\x03 Type H \x0e %oD0fxvc7hUOX_305zIXIlg  x\x04 Value C T
  ```
  The length-prefixed element/attribute names and the `eSpaceFragment` root element are plainly visible.

**Fragment names observed in this module (all 93, deduplicated by category) — [VERIFIED LOCALLY]**

Singleton fragments: `eSpace` (16,293 B), `Structures`, `AnonymousStructures`, `ListTypes`, `References`
(5,368,717 B — by far the largest, 65% of the module), `CompilationUnits` (108,685 B), `SoftwareUnits`,
`Signature` (30,759 B), `Versions`, `RebindData`, `VerifyCaches`, `ReferersForCompilerData`, `ReferersData`
(232,402 B), `LicensedFeatures`, `UnusedDependencies`, `ClientVariables`, `EntityDiagrams`, `Images`,
`ModelFeatures`, `EspaceConfigurations`, `UserActions`.

Keyed/per-object fragments use the form `Category#<base64ish-22-char-key>`:
`Widgets#<key>`, `UserActions#<key>`, `ClientActionFlows#<key>`, `NodesNotShownInESpaceTree#<key>`
(the bulk of the 93), and nested keys like
`NodesNotShownInESpaceTree#B4kRGvrnOEmQonA8ir4Pyg.#FlowExceptionHandler`.

This independently corroborates the community claim that "a section about a Server Action is part of a fragment
called `UserActions.xml`" — [OutSystems forum: OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/) /
[DEV: The OutSystems Model](https://dev.to/outsystems/the-outsystems-model-abstracting-low-code-into-a-visual-language-498p).

**Recoverable content, demonstrated by plain `strings` on decoded fragments — [VERIFIED LOCALLY]**

`eSpace.fi` yields module-level settings verbatim:
```
ESpace / Key: Am0mHuuAS0yPh37L4weNBQ / GeneralHash / LastModifiedByCommand
Name: TestApplication / Description: "An application to "
UserProviderESpaceName: Users / UserProviderESpaceKey: WWAQZTkE5UuwES8B+6Svpg
DefaultThemeNewRuntime: NewRuntime.Theme:/NRThemes.EHWy15q2lEymE4eJ_Th8yQ
PreviousDefaultScreenValue.Name: Screen1 ... UsedInReference: MainFlow\Screen1
GlobalErrorHandler: NRFlows.FlowExceptionHandlingFlow:/NRWebFlows.B4kRGvrnOEmQonA8ir4Pyg/FlowExcepti...
DefaultTransition: Fade
MandatoryValidatorMsg: "This field is required."
IntegerValidatorMsg: "Enter a valid integer."
DecimalValidatorMsg / CurrencyValidatorMsg / DateValidatorMsg ...
```

`Structures.fi` yields a structure definition with attributes:
```
eSpaceFragment / Count=1 / Structure / Key: ZI9jwb4A+0WKdGXPzeBBrg
LastModifiedDate: 2016-02-26 17:43:46 / Public: Yes
Name: MasterDetailItem
TextResources / Metadata / Attributes / StructureAttribute
  Id: xSyJp25t3EqBEERCeesiGw / Label / Type: %H6G+eTAigEi7LPUbg3Ey0g / Length
```

`ClientActionFlows#p7Wmv16Tnk6xpQmiB99SaQ.fi` yields an action with its signature:
```
Count=3 / NRFlows.ClientActionFlowInsideFolder / Key: FS48A55jqU+m6GmdxDR29A
DebuggerHash / LastModifiedDate: 2016-10-10 09:40:47
Name: OfflineDataSync
Description: "Action which executes the offline data synchronization."
IsAsync: Yes / Image / TextResources
NodesShownInESpaceTree / NodesNotShownInESpaceTree / HasChildren
LocalVariables / InputParameters / Variables.GenericInputParameter
  piuR+_uyVECxQTnieUpu8Q / SyncUnit / IsMandatory
```

`ClientVariables.fi`: `Variables.ClientVariable / Name: LastURL / Type: %uROOBXPvQEyU76NWO+1uxQ / DefaultValue`

### Inferences

- Types are **not inline**; they are references to keys (`Type: %H6G+eTAigEi7LPUbg3Ey0g`, prefix `%`). A full
  parser must build a key→object map across all fragments and resolve these. The `#`/`%`/`|`/`/` prefixes are
  sigils in OutSystems *compound keys* (cf. `OutSystems.MetaModel.CompoundKeys.RootCompoundKey` leaked in the header).
- The `References` fragment dominating 65% of a trivial module explains why even "empty" OML files are multi-MB:
  it embeds the full public interface of every referenced producer module (OutSystems UI, etc.).
- `Signature` as a dedicated 30 KB fragment plus `APIHash`/`ContentHash` in the manifest means tamper-evidence
  exists at both layers; re-packing an edited OML will likely need those recomputed (untested).
- Expression logic is present as `ParsedExpression` subtrees (seen in the Widgets fragment) — i.e. expressions are
  stored **pre-parsed as ASTs**, not as source strings, so recovering readable expression text requires
  re-serializing the AST, not just reading an attribute.

### Gaps

- The first 1,492 bytes of the inflated blob (the preamble before the directory, including a 93-byte
  high-entropy block prefixed by `5d 00 00 00`) are **not identified**. Candidates: an integrity hash/signature,
  or a small index. I did not resolve it, and I will not guess.
- I did not decode the Fast Infoset documents into true XML (Python has no stdlib Fast Infoset decoder). Element
  and attribute *names and values* are recoverable with a strings pass, but correct tree structure, the
  vocabulary/string tables, and typed values require a real FI decoder (e.g. Noemax.FastInfoset, or
  Sun/Glassfish `FastInfoset` on the JVM).
- The exact meaning of header fields 3 (`155`), 5, 6 and 10 is inferred from position only, not documented.

---

## Q3: Is OML content encrypted or merely serialized? Known keys? Published parser or spec?

### Takeaway

Merely serialized and compressed — **no encryption, no keys involved**. No official spec exists; OutSystems
states the XML form is internal and unsupported. The one real open-source parser is `oml-utilities`, and it works
by *reflecting into OutSystems' own shipped DLLs* rather than reimplementing the format.

### Cited Findings

- **Not encrypted** — entropy 6.37 bits/byte, 112,668 plaintext ASCII runs, Fast Infoset magic on all 93 bodies. **[VERIFIED LOCALLY]** (see Q2). There is no key to find; "protected only by obscurity" is the accurate characterization.
- **No official spec.** OutSystems has published no OML format specification; the Forge OML Utilities listing itself carries the standard **"not supported by OutSystems"** disclaimer — [Forge: OML Utilities / OML2XML](https://www.outsystems.com/forge/component-overview/10885/oml2xml)
- Community/MVP position: "An .oml (OutSystems Modeling Language) file contains a XML representation of the visual elements in a module" and **"The only way to read/edit it is Service Studio / ODC Studio"** — Nuno Reis (MVP), [OutSystems forum: OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/)
- The XML form "is internal and not supported as a feature", so it can change between major versions without notice — [OutSystems forum: Can I see the source code of .oml file](https://www.outsystems.com/forums/discussion/76283/can-i-see-the-source-code-of-oml-file/)
- **Sources openly conflict on "binary vs XML"**: Manikandan Sambasivam calls it "a binary file format used to represent an application module", while Nuno Reis calls it XML — both on [the same thread](https://www.outsystems.com/forums/discussion/100942/oml-data/). My local analysis **resolves the conflict**: both are right at different layers — the *container* is binary (magic + deflate), the *content* is XML in Fast Infoset binary encoding. **[VERIFIED LOCALLY]**
- Even the acronym is unsettled in the community — "Markup Language", "Modeling Language", and "Module Language" all appear: [OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/), [what is full form of oml](https://www.outsystems.com/forums/discussion/32817/what-is-full-form-of-oml/)
- A standing feature request for a supported OML API exists — [OutSystems Ideas: OML API / accessing data](https://www.outsystems.com/ideas/5948/oml-api-accessing-data/)
- An earlier OML↔XML Forge converter **was withdrawn**: Nuno Reis, "That component was removed." — [OML data thread](https://www.outsystems.com/forums/discussion/100942/oml-data/); see also [OML to XML](https://www.outsystems.com/forums/discussion/100962/oml-to-xml/) and [Inspect the OML file](https://www.outsystems.com/forums/discussion/5476/inspect-the-oml-file/)
- Community caveat on parsing the exported XML: "the XML don't follow a specific pattern for each element", making generic parsing hard — [Read and Display OML File as Text](https://www.outsystems.com/forums/discussion/96092/read-and-display-oml-file-as-text/)

### Inferences

- Because `oml-utilities` reflects into OutSystems' own DLLs, OutSystems can break every community tool with a
  point release — which is exactly what the "internal and not supported" wording reserves the right to do.
- Conversely, since there is no crypto, a *clean-room* parser (deflate + Fast Infoset + fragment framing, as
  derived above) is entirely feasible and would be immune to DLL/version coupling.

### Gaps

- I found no published formal grammar for the Fast Infoset *vocabulary* OutSystems uses (the element/attribute
  name set per model version). It would have to be induced empirically per platform version.

---

## Q4: What does the OutSystems model object graph look like? BinaryFormatter, protobuf, custom, XML?

### Takeaway

**None of BinaryFormatter or protobuf.** The model is a C#-class object graph in memory, persisted as **XML**,
physically encoded as **Fast Infoset binary XML**, split into named fragments, and raw-deflated. The only
.NET-style serialization present is Newtonsoft.Json (with `$type`/`$id`/`$ref`) — and that is used for Service
Studio *UI/presenter state in the header*, not for the model itself.

### Cited Findings

- Official OutSystems engineering description: models have "an in-memory representation as C# class instances and an **xml-based persistent representation**", and the OML is "a compressed file composed of several fragments" — [DEV Community (OutSystems org): The OutSystems Model: Abstracting low-code into a visual language](https://dev.to/outsystems/the-outsystems-model-abstracting-low-code-into-a-visual-language-498p); related: [OutSystems Language VS OutSystems Model (Medium, César Afonso)](https://medium.com/cesarafonso/outsystems-language-vs-outsystems-model-60505d8c857e)
- **Physical encoding is Fast Infoset, not textual XML** — all 93 fragment bodies carry `E0 00 00 01`. **[VERIFIED LOCALLY]** This is the key correction to the common community claim that "OML is XML".
- The community tool bundles **`Noemax.FastInfoset.4.1.5.dll`** and `Noemax.FastInfoset.Net4.18.14.5339.dll` as embedded resources alongside the OutSystems assemblies — independent corroboration that Fast Infoset is the OML encoding. **[COMMUNITY]** — [oml-utilities .csproj](https://github.com/kelter-antunes/oml-utilities)
- It likewise bundles **`ICSharpCode.SharpZipLib.0.85.5.dll`** and `ICSharpCode.SharpZipLib.1.1.0.dll` — corroborating the DEFLATE layer. **[COMMUNITY]** — same source
- Internal namespace evidence from the header's base64 JSON: `OutSystems.MetaModel`, `OutSystems.MetaModel.CompoundKeys.RootCompoundKey`, `ServiceStudio.Presenter`, `ServiceStudio.Framework`, `ServiceStudio.WeakReferences.AbstractObjectIdentifier`, with `ownerESpaceInstanceId` as a GUID (`a584d8ad-1273-41a7-ace9-46990e067c6a`). **[VERIFIED LOCALLY]**
- The reader entry point in OutSystems' own API surface is the class **`OutSystems.Oml.Oml` in `OutSystems.Common.dll`**, constructed as `new Oml(stream, false, null, null)`, exposing `DumpFragmentsNames()`, `GetFragmentXmlReader(fragmentName)` (whose result has `ToXElement()` and `Close()`), `WriteTo(stream)`, and a `Header` object with fields `Name`, `Description`, `Version`, `LastUpgradeVersion`, `LastModifiedUTC`, `ActivationCode` (read-only), `Signature` (read-only), `NeedsRecover` — **[COMMUNITY, read from source]** [Oml.cs](https://github.com/kelter-antunes/oml-utilities/blob/master/OML%20Utilities/Core/Oml.cs), [OmlFragmentReader.cs](https://github.com/kelter-antunes/oml-utilities/blob/master/OML%20Utilities/Core/OmlFragmentReader.cs), [OmlHeader.cs](https://github.com/kelter-antunes/oml-utilities/blob/master/OML%20Utilities/Core/OmlHeader.cs)
- Fragment root element is `eSpaceFragment` with a `Count` attribute; objects inside are typed by qualified names like `Variables.ClientVariable`, `Variables.GenericInputParameter`, `Flows.EntityDiagram`, `Structure`, `StructureAttribute`, `NRWebWidgets.CustomWidget`. **[VERIFIED LOCALLY]**
- Every model object carries `Key`, plus hashes `GeneralHash` / `DebuggerHash`, and audit fields `CreatedBy`, `LastModifiedBy`, `LastModifiedByCommand`, `LastModifiedDate`. **[VERIFIED LOCALLY]**

### Inferences

- `LastModifiedByCommand` keys suggest the model is edited via a command/undo pattern whose command IDs are persisted — useful for change attribution if one wanted to diff OMLs.
- `GeneralHash` vs `DebuggerHash` being separate implies hash-based incremental compile and debug-symbol matching; fragment-level granularity is almost certainly what enables Service Studio to send only changed fragments on publish.
- Fast Infoset + fragment-level framing is a deliberate performance design (open/save large models fast), not an anti-reverse-engineering measure.

### Gaps

- I could not enumerate the full model type vocabulary (every `Flows.*`, `Variables.*`, `Widgets.*` class name) because that needs a real FI decode plus a non-trivial sample app. The sample here had no Entities fragment, so entity/attribute structure is only inferred from `Structures`/`EntityDiagrams`.

---

## Q5: Concrete open-source projects, gists, blog posts, forum threads

### Takeaway

The ecosystem is thin: essentially one real OML parser lineage (`oml-utilities`, DLL-reflection based, O9.1/O10/O11),
one Service-Studio-driven CLI (`oml-cli`, Model API based, no format parsing), and a handful of forum threads. The
original Forge converter was removed.

### Cited Findings

| Project / source | What it is | URL | Status |
|---|---|---|---|
| **`caiosm1005/oml-utilities`** | Original source of the Forge "OML Utilities" asset | linked from the Forge page; **GitHub API returned 404 for `caiosm1005/oml-utilities` when I queried it on 2026-10-21** — repo appears gone/renamed | [Forge listing](https://www.outsystems.com/forge/component-overview/10885/oml2xml) |
| **`kelter-antunes/oml-utilities`** | Live fork, `master`, 19 commits — the most usable copy | https://github.com/kelter-antunes/oml-utilities | **[VERIFIED: reachable, source read]** |
| **`silviogarbes/oml-utilities`** | Another fork, same description | https://github.com/silviogarbes/oml-utilities | [COMMUNITY] |
| **`Topurrra/oml-cli`** | "CLI and agent skill to build and edit OutSystems 11 modules safely through Service Studio's Model API" — **drives Service Studio; does not parse OML XML** | https://github.com/Topurrra/oml-cli | [COMMUNITY] |
| **OutDoc** | Documentation generator that consumes the simplified XML export | referenced in [Can I see the source code of .oml file](https://www.outsystems.com/forums/discussion/76283/can-i-see-the-source-code-of-oml-file/) | [COMMUNITY] |

**`oml-utilities` verified source facts** — [GitHub, read directly](https://github.com/kelter-antunes/oml-utilities):

- Embedded OutSystems assemblies (this is the actual version matrix it supports):
  `OutSystems.Common.9.1.603.0.dll`, `OutSystems.Common.10.0.303.0.dll`, **`OutSystems.Common.11.0.520.0.dll`**,
  and matching `OutSystems.RuntimeCommon.{9.1.603.0,10.0.303.0,11.0.520.0}.dll`.
- Plus `Noemax.FastInfoset.4.1.5.dll`, `Noemax.FastInfoset.Net4.18.14.5339.dll`,
  `ICSharpCode.SharpZipLib.{0.85.5,1.1.0}.dll` — the FI + deflate stack.
- Other deps: CommandDotNet 2.8.0, FluentValidation 7.6.103, Humanizer.Core 2.5.16.
- Source files: `Core/Oml.cs`, `Core/OmlHeader.cs`, `Core/OmlFragmentReader.cs`, `Core/OmlFragmentWriter.cs`, `Core/AssemblyUtility.cs`, `Core/PlatformVersion.cs`, `OmlUtilities.cs`, `ProgramWorker.cs`.
- README: "Any operation that involves reading or manipulating an OML file must specify the target platform version", labelled `O9.1`, `O11`, etc., because it is "needed in order to load the correct DLL assemblies for decoding the contents of the OML file."
- Commands: `Manipulate` (with `--format xml`, `-H "<HeaderName>:<HeaderValue>"`, `-F "<FragmentName>:<FragmentXmlContent>"`), `ShowPlatformVersions` (`--fullversion`, `--latest`), `ShowHeaders`, `TextSearch` (case sensitive, searches a whole directory of OMLs).
- `GetXml()` wraps all fragments under a single root `<OML>` element, adding a `FragmentName` attribute to each — so its XML output shape is `<OML><...FragmentName="eSpace"/>...</OML>`.

**Concrete command examples**

Pure-open-source, no OutSystems software required (derived from my analysis — **[VERIFIED LOCALLY]**):

```bash
# 1. Unpack the .oap (plain ZIP)
unzip -o "Test Application.oap" -d ./oap_extracted
# -> Manifest.xml  +  <Solution>/<Module>.oml

# 2. Confirm the OML magic and header
xxd ./oap_extracted/Test_Application/TestApplication.oml | head -4   # "OML{..."

# 3. Split header / inflate payload / dump all fragments
python3 - <<'PY'
import struct, zlib, re, os
src = './oap_extracted/Test_Application/TestApplication.oml'
d = open(src,'rb').read()
assert d[:3] == b'OML', 'not an OML'
hlen = struct.unpack('<I', d[3:7])[0]
header = d[7:7+hlen].decode('utf8')
print('header fields:', header.split('|')[:10])
blob = zlib.decompressobj(-15).decompress(d[7+hlen:])   # RAW deflate
# fragment directory: 93 x [u32 nameLen][name][u32 contentLen], starting at 1492
off, ents = 1492, []
while off + 8 <= len(blob):
    nl = struct.unpack('<I', blob[off:off+4])[0]
    if not 1 <= nl <= 200: break
    nm = blob[off+4:off+4+nl]
    if not re.fullmatch(rb'[\x20-\x7e]+', nm): break
    cl = struct.unpack('<I', blob[off+4+nl:off+8+nl])[0]
    ents.append((nm.decode(), cl)); off += 8 + nl
cur = off
os.makedirs('frags', exist_ok=True)
for nm, cl in ents:
    body = blob[cur:cur+cl]
    assert body[:4] == b'\xe0\x00\x00\x01', nm      # Fast Infoset magic
    open('frags/' + re.sub(r'[^\w.#+-]','_',nm)[:80] + '.finf','wb').write(body)
    cur += cl
print(len(ents), 'fragments;', 'exact EOF' if cur == len(blob) else 'MISMATCH')
PY

# 4. Cheap content recovery with no FI decoder at all
strings -n 4 frags/eSpace.finf | head -40
strings -n 4 frags/Structures.finf
```

> Caveat on step 3: the directory start offset `1492` is the value measured on this file. A robust implementation
> should **scan** offsets 0..~8192 for the longest self-consistent directory whose declared lengths sum exactly to
> `len(blob) - dir_end` and whose every body starts with `E0 00 00 01` — that is the test I used, and it is
> unambiguous.

Using the community tool instead (Windows/.NET, per its README) — **[COMMUNITY]**:

```bash
OmlUtilities.exe ShowPlatformVersions --latest
OmlUtilities.exe ShowHeaders -v O11 "TestApplication.oml"
OmlUtilities.exe Manipulate -v O11 "TestApplication.oml" "out.xml" --format xml
OmlUtilities.exe TextSearch -v O11 ./modules "SomeKeyword"
```

### Inferences

- `oml-utilities` only embeds `OutSystems.Common.11.0.520.0.dll`, but my sample was produced by platform
  `11.55.93.65333` / OML version `11.0.415.100`. Given the README's version-gating, an old build is a real risk of
  "UnsupportedNewerVersion" on current O11 files — the clean-room approach above has no such limitation.
- The disappearance of the upstream repo and the removal of the Forge converter make the clean-room route the more
  durable one.

### Gaps

- I could not verify `caiosm1005/oml-utilities` contents (GitHub API 404 at time of research) nor whether the
  forks diverge. I did not find any conference talk or dedicated blog post on OML byte-level internals.
- No `.oml` **writer** path verified: `OmlFragmentWriter` and `WriteTo` exist, but whether `Signature`/
  `GeneralHash`/`APIHash` must be recomputed for a repacked OML to be publishable is **untested**.

---

## Q6: What can be recovered WITHOUT Service Studio vs. what requires Service Studio / Platform Server?

### Takeaway

Far more than the community believes: with no OutSystems software at all, the `.oap` manifest and the entire OML
fragment set — including action names, structures, variables, module settings and expression ASTs — are
recoverable, because there is no encryption. What still requires OutSystems software is faithful XML
reconstruction via its own decoder, a visual/semantic view, and anything executable.

### Cited Findings

**Recoverable with only `unzip`, `zlib` and a Fast Infoset decoder — [VERIFIED LOCALLY]**

- Whole `.oap`/`Manifest.xml`: app name/description, module inventory, reference graph, `ApplicationKind`, `PrimaryColor`, `TemplateKey`, hashes, `OriginEnvironmentCode`, and the app **icon as inline base64 PNG**.
- OML header: OML format version, producing Service Studio version, module UIDs, name, description, last-modified timestamp, and the base64 Service Studio presenter/UI state.
- All 93 fragment names and bodies, i.e. the full model surface: `eSpace`, `Structures`, `AnonymousStructures`, `ListTypes`, `References`, `CompilationUnits`, `SoftwareUnits`, `Signature`, `ClientVariables`, `EntityDiagrams`, `Images`, `ModelFeatures`, `EspaceConfigurations`, `UserActions`, `UserActions#<key>`, `ClientActionFlows#<key>`, `Widgets#<key>`, `NodesNotShownInESpaceTree#<key>`.
- Demonstrated concrete recoveries without any OutSystems code: structure `MasterDetailItem` with its attributes; client action `OfflineDataSync` with description, `IsAsync`, input parameter `SyncUnit` and `IsMandatory`; client variable `LastURL`; module default theme, default screen `MainFlow\Screen1`, global error handler path, and all validation messages.

**Requires OutSystems' own assemblies (`OutSystems.Common.dll`) — [COMMUNITY]**
- Byte-faithful fragment→XML conversion via `GetFragmentXmlReader(...).ToXElement()`; version-correct decoding is DLL-gated by design — [Oml.cs](https://github.com/kelter-antunes/oml-utilities/blob/master/OML%20Utilities/Core/Oml.cs), [oml-utilities README](https://github.com/kelter-antunes/oml-utilities)
- Note this is **not** full Service Studio — just the redistributed `OutSystems.Common` / `OutSystems.RuntimeCommon` DLLs, which `oml-utilities` embeds for 9.1/10/11.

**Requires Service Studio / ODC Studio — [COMMUNITY]**
- Visual editing and the authoritative view: "The only way to read/edit it is Service Studio / ODC Studio" — Nuno Reis (MVP), [OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/)
- Safe programmatic *editing* at model level: `oml-cli` works "through Service Studio's Model API" and "never edits OML XML" — https://github.com/Topurrra/oml-cli

**Requires Platform Server — [DOCUMENTED]**
- Actually deploying a pack: the Solution Pack Tool "publishes OutSystems solutions on an environment", taking `.osp` or `.oap` — [OutSystems 10 docs](https://success.outsystems.com/documentation/10/setting_up_outsystems/unattended_installation_and_upgrade/unattended_installation_and_upgrade_for_java/solution_pack_tool_command_line_reference_for_java/)
- Compiling the model to runnable .NET/Java and resolving `CompilationUnits` is a Platform Server function (the OML carries `CompilationUnits`/`SoftwareUnits` metadata, not compiled output). **[VERIFIED LOCALLY that the fragments exist]**; that compilation itself needs the server is **[INFERENCE]**.

### Inferences

- The practical ceiling for a no-OutSystems toolchain is a **readable model dump and static analysis**
  (inventory, dependency graph, naming/lint checks, diffing between OML versions) — this is clearly achievable now.
- Full fidelity *round-trip editing* without OutSystems software is the risky part, because of `Signature` and the
  per-object `GeneralHash`/`DebuggerHash`.
- Expression *text* (e.g. the source of an If condition) will be the hardest recovery target, since expressions are
  stored as `ParsedExpression` ASTs with type references by key.

### Gaps

- I could not test whether a hand-repacked `.oap`/`.oml` is accepted by Service Studio or the Platform Server.

---

## Q7: Version differences across OutSystems 9/10/11 and ODC

### Takeaway

The OML container has been stable enough across 9.1/10/11 that one tool handles all three, but **decoding is
explicitly version-gated** and the internal XML is unsupported and free to change. ODC is a genuinely different
world: no `.oap` export, no "modules", and `.oml` used for apps/libraries — but I could not find an official ODC
packaging spec.

### Cited Findings

**O9 / O10 / O11 — [COMMUNITY]**
- A single tool supports all three by embedding `OutSystems.Common` **9.1.603.0 / 10.0.303.0 / 11.0.520.0**, and it requires the caller to name the version (`O9.1`, `O11`) "in order to load the correct DLL assemblies for decoding the contents of the OML file" — [oml-utilities](https://github.com/kelter-antunes/oml-utilities)
- The two Fast Infoset DLL generations (`Noemax.FastInfoset.4.1.5` vs `Noemax.FastInfoset.Net4.18.14.5339`) and two SharpZipLib generations (`0.85.5` vs `1.1.0`) bundled side by side imply the FI/deflate library versions differ by platform era — [oml-utilities .csproj](https://github.com/kelter-antunes/oml-utilities)
- The internal XML "is internal and not supported as a feature" and can change between major versions without notice — [OutSystems forum](https://www.outsystems.com/forums/discussion/76283/can-i-see-the-source-code-of-oml-file/)

**O11, this sample — [VERIFIED LOCALLY]**
- `Manifest.xml`: `Schema="3"`, `HubServerVersion="11.42.1.47790"`, `LastUpgradeVersion="11.0.0.200"`
- OML header: format version `11.0.415.100`, producer `11.55.93.65333`, third field `155`
- `Oml` exposes both `Version` and `LastUpgradeVersion`, and an `UnsupportedNewerVersion` exception exists in the load path — i.e. OutSystems' own loader refuses OMLs newer than the assembly — [Oml.cs](https://github.com/kelter-antunes/oml-utilities/blob/master/OML%20Utilities/Core/Oml.cs), [OmlHeader.cs](https://github.com/kelter-antunes/oml-utilities/blob/master/OML%20Utilities/Core/OmlHeader.cs)

**ODC — [DOCUMENTED] + [COMMUNITY]**
- Officially: "the concept of module doesn't exist in ODC, the equivalent concept is called an **asset**" — [ODC docs: ODC for O11 developers](https://success.outsystems.com/documentation/outsystems_developer_cloud/odc_for_o11_developers/)
- `.oap` export is **not supported in ODC**; community answer: "in ODC that is not a thing. You only have application (.oml) or library (.oml) and both can be published to the Forge" — [OutSystems forum: How to Export an Application as .oap File in OutSystems ODC?](https://www.outsystems.com/forums/discussion/103104/how-to-export-an-application-as-oap-file-in-outsystems-odc/). **Flagged: I consider this only partially reliable** — the thread does not settle it and the original search result noted the `.oml` wording looks like it may be a typo.
- ODC "external logic" (custom C#) is packaged as a **plain `.zip`** uploaded to the ODC Portal, not an OutSystems-specific container — [ODC docs: External libraries SDK README](https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/extend_your_apps_with_custom_code/external_libraries_sdk_readme/); example: "upload `UltimatePDF_ExternalLogic.zip` to the ODC Portal as external logic" and "Use ODC Studio to publish the modules as .oml files" — [OutSystems/UltimatePDF-ExternalLogic](https://github.com/OutSystems/UltimatePDF-ExternalLogic)
- ODC mobile output is a separate concern with its own documented packaging flow — [ODC docs: Create mobile app package](https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/mobile_apps/create_mobile_app_package/)
- On the O11 side, an `.oml` "contains a XML representation of the visual elements in a module (O11) or **application (ODC)**" — i.e. the same extension spans both products with different unit semantics — [OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/)

### Inferences

- Since ODC Studio still emits `.oml`, the `OML` magic + deflate + Fast Infoset pipeline **plausibly** carries over
  to ODC with a different vocabulary and version stamp. **This is [SPECULATION]** — I had no ODC `.oml` to test and
  found no source confirming it.
- ODC's drop of `.oap`/`.osp` fits its managed-deployment model: there is no customer-run Platform Server for a
  Solution Pack Tool to target.

### Gaps

- **No official ODC packaging specification found.** The ODC docs I reached describe external-library `.zip` and
  mobile packages, not an application-package format. The `.oap`-not-supported claim rests on a forum answer only.
- I verified no ODC `.oml` byte layout, and no O9/O10 sample, so cross-version container differences are
  inferred from the tool's version-gating rather than measured.

---

## Q8: What do the forums/community say, and are there official "proprietary/unsupported" statements?

### Takeaway

The community consensus is "you can't read it, use Service Studio", and it is partly wrong — but the *support*
position is unambiguous: the format and its XML projection are internal, unsupported, and subject to change, and
the Forge tooling carries an explicit no-support disclaimer. There is no official statement publishing or
blessing the format.

### Cited Findings

- Forge disclaimer: the OML Utilities asset "is not supported by OutSystems" — [Forge: OML Utilities / OML2XML](https://www.outsystems.com/forge/component-overview/10885/oml2xml)
- "The XML is internal and not supported as a feature" — [Can I see the source code of .oml file](https://www.outsystems.com/forums/discussion/76283/can-i-see-the-source-code-of-oml-file/)
- "The only way to read/edit it is Service Studio / ODC Studio" — Nuno Reis (MVP), [OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/)
- "That component was removed" (on the former OML↔XML converter) — Nuno Reis, [OML data](https://www.outsystems.com/forums/discussion/100942/oml-data/)
- "There is no direct tool from OutSystems for converting OML to XML" — [OML to XML](https://www.outsystems.com/forums/discussion/100962/oml-to-xml/)
- A simplified XML export does exist and is what OutDoc uses — [Can I see the source code of .oml file](https://www.outsystems.com/forums/discussion/76283/can-i-see-the-source-code-of-oml-file/)
- Parsing complaint: "the XML don't follow a specific pattern for each element" — [Read and Display OML File as Text](https://www.outsystems.com/forums/discussion/96092/read-and-display-oml-file-as-text/)
- Long-running desire for a supported path — [OutSystems Ideas: OML API / accessing data](https://www.outsystems.com/ideas/5948/oml-api-accessing-data/); historical thread [Inspect the OML file (2011-era)](https://www.outsystems.com/forums/discussion/5476/inspect-the-oml-file/)
- OutSystems' own engineering content *does* describe the fragment architecture publicly — "a compressed file composed of several fragments" with an "xml-based persistent representation" — [DEV Community (OutSystems): The OutSystems Model](https://dev.to/outsystems/the-outsystems-model-abstracting-low-code-into-a-visual-language-498p)
- **Third-party file-info sites are unreliable here.** [convert.guru's OML page](https://convert.guru/oml-converter) describes OML as closed and openable only by Service Studio; [fileinfo.com/extension/oml](https://fileinfo.com/extension/oml) and [fileproinfo.com](https://fileproinfo.com/file-type/oml) also conflate OutSystems OML with an unrelated "Printer Media Profile" OML. My local analysis contradicts the "only Service Studio" framing. Do not cite these as authorities.

### Inferences

- OutSystems' public position is *non-support*, not legal prohibition — I found no statement claiming the format is
  protected by anything beyond being proprietary and undocumented. (I am not offering a legal opinion; licence terms
  for the redistributed `OutSystems.Common.dll` were not reviewed and are a real consideration for any tool that
  embeds them.)
- The gap between community belief ("unreadable") and reality (no encryption; fully parseable) exists mainly because
  nobody published the container layout. The directory + Fast Infoset framing in Q2 closes that gap.

### Gaps

- I found no Stack Overflow question on OML byte-level internals (the suggested `outsystems`-tagged SO search
  surfaced nothing relevant in my results).
- No OutSystems official page states "the OML format is proprietary" in those words; the support position is
  expressed through the Forge disclaimer and the "internal and not supported" forum wording instead.

---

## Reproducibility appendix

Artifacts produced during this research (scratchpad, session-local):

```
/private/tmp/claude-503/.../scratchpad/oapx/
  Manifest.xml                                  186,445 B   (from the .oap)
  Test_Application/TestApplication.oml         3,053,090 B
  inflated.bin                                 8,185,876 B   (raw-deflate output)
  frags/*.finf                                 93 files      (Fast Infoset fragment bodies)
```

Key verified constants for the sample file:

| Quantity | Value |
|---|---|
| `.oap` size / entries | 3,096,013 B / `Manifest.xml` + 1 `.oml` |
| ZIP archive comment | `The Solution Pack Manifest` |
| OML magic | `4F 4D 4C` (`OML`) at offset 0 |
| Header length (uint32 LE @ 0x03) | 36,219 |
| Payload start | 36,226 |
| Compression | raw DEFLATE (`wbits=-15`), no zlib/gzip header |
| Inflated size | 8,185,876 B |
| Inflated entropy (first 200 KB) | 6.37 bits/byte (→ not encrypted) |
| Fragment directory start / end | 1,492 / 5,524 |
| Fragment count | 93 (93/93 begin `E0 00 00 01`) |
| Σ fragment lengths | 8,180,352 = 8,185,876 − 5,524 (exact) |
