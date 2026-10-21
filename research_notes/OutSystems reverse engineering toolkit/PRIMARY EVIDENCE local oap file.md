# Primary evidence: hands-on inspection of a real OutSystems .oap

**Source:** not web research. Direct inspection of the user's own file
`/Users/I5285/Documents/GitHub/Outsystem-ReverseEngineering/Test Application.oap`
(3,096,013 bytes), by the coordinator on 2026-10-21, independently re-verified after
the format researcher's findings. Measured facts about one O11 package.

> **CORRECTION NOTICE — an earlier revision of this file was wrong.**
> It concluded the `.oml` was "not encrypted and not compressed," reasoning from a
> 0.387 printable-byte ratio and a failed deflate search. **The deflate search was
> the error: it scanned only offsets up to +64 from the magic, but the plaintext
> header is 36,219 bytes long, so the compressed stream begins at offset 36,226 —
> far outside the window.** The file IS raw-deflate compressed. The "not encrypted"
> half of that conclusion stands. Corrected and re-verified below. Do not carry the
> "uncompressed" claim, nor the "0x8d = 141 length" misreading, into the report.

## 1. .oap container = plain ZIP (verified)

`file` reports `Zip archive data, at least v2.0 to extract, compression method=deflate`.
`unzip` opens it with no password. 3 entries:

| Size | Path |
|---|---|
| 186,445 | `Manifest.xml` |
| 0 | `Test_Application/` (dir) |
| 3,053,090 | `Test_Application/TestApplication.oml` |

The ZIP archive comment is the literal string `The Solution Pack Manifest` — a clean
fingerprint for OutSystems packs. No extraction barrier at this layer.

## 2. Manifest.xml is readable XML — immediately usable, zero tooling

Verbatim head:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Pack Schema="3" HubServerVersion="11.42.1.47790" LastUpgradeVersion="11.0.0.200"
      IsApplicationPack="true" UID="+5oc2juJUkaapQxfdR6pmw" Creation="2026-10-21 11:18:18">
  <Solutions>
    <Solution Schema="3" HubServerVersion="11.42.1.47790" UID="JDeiRWI8dUqsENq57vN8yg"
              Creation="2026-10-21 11:18:17" Name="Test_Application"
              Description="An application to " ActivationCode="" IsTransient="true">
      <References>
        <Reference UID="Am0mHuuAS0yPh37L4weNBQ" Kind="eSpace" Name="TestApplication"
                   Description="An application to ">
          <LogicalDatabases />
          <DBCatalog LogicalName="" />
        </Reference>
      </References>
      <Applications>
        <Application UID="JDeiRWI8dUqsENq57vN8yg" Name="Test Application"
                     Description="An application to "
                     FrontOfficeEspaceKey="Am0mHuuAS0yPh37L4weNBQ"
                     FrontOfficeEspaceName="TestApplication" BackOfficeEspaceName=""
                     TemplateKey="Wrm0V2ZyskqM7KobRok75w" PrimaryColor="#FFB61E"
                     APIHash="591279d1-98c0-d3da-cb17-78c37ebe9f64"
                     ContentHash="725d1ea1-5093-8ec0-78bb-ddbefd60015a"
                     OriginEnvironmentCode="BY0.N5U.BAT.OHU.EZF.OZS.KPW.AUT"
                     ForgeBaseVersion="0.0" OutdatedReferences="false"
                     ApplicationKind="CrossDevice">
```

186 KB of manifest for a *single-module* app, so it carries real structure beyond this
header. Recoverable with any XML library: module inventory, eSpace reference/dependency
graph, `ApplicationKind`, theme colour, origin environment, schema + server versions,
stable UIDs. `IsApplicationPack` is the `.oap` vs `.osp` discriminator.

## 3. The .oml format — decoded and verified

| Offset | Size | Content |
|---|---|---|
| 0x00 | 3 | ASCII magic `OML` (`4F 4D 4C`) |
| 0x03 | 4 | uint32 **LE** header length = `0x8D7B` = **36,219** |
| 0x07 | 36,219 | plaintext ASCII `\|`-delimited header |
| 36,226 | remainder | **raw DEFLATE** (`wbits=-15`, no zlib/gzip wrapper) |

Re-verified by the coordinator:
- `magic: b'OML'`; `uint32 LE at 0x03 = 36219 (0x8d7b)`; body starts at 36,226.
- `zlib.decompressobj(-15)` on `d[36226:]` inflates cleanly to **8,185,876 bytes**
  (2.68× the 3,053,090-byte file).

### Inflated blob layout (verified)
- `[0 .. 1491]` — opaque preamble, **unidentified**. Contains a 93-byte high-entropy
  block prefixed `5d 00 00 00`; possibly a hash or signature. Not guessed at.
- `[1492 .. 5523]` — **fragment directory**: 93 records of
  `[uint32 nameLen][name ASCII][uint32 contentLen]`.
- `[5524 .. EOF]` — 93 concatenated **Fast Infoset** documents (ITU-T X.891 binary XML),
  each beginning `E0 00 00 01`.

**Self-consistency proof (reproduced by the coordinator, not taken on trust):**
93 fragments parsed; `sum(contentLen) = 8,180,352`; directory ends at 5,524;
`5,524 + 8,180,352 = 8,185,876 == len(blob)` → **exact, zero slack.**

### Fragment inventory (measured)
Largest five:

| Fragment | Bytes |
|---|---|
| `References` | 5,368,717 |
| `Resources` | 1,971,193 |
| `ReferersData` | 232,402 |
| `CompilationUnits` | 108,685 |
| `Widgets#+Sc1+XsmWUiszZQMKnQqBw` | 92,531 |

`References` alone is **65% of a trivial module**, because it embeds every producer's
public interface. This is the dominant cost driver in any OML-based pipeline and a
strong argument for extracting a module's *own* fragments and resolving references
separately.

Naming scheme: singletons (`eSpace`, `Structures`, `References`, `CompilationUnits`,
`Resources`, `ReferersData`, `UnusedDependencies`, `UserActions`, `Signature`) plus
key-suffixed fragments `<Collection>#<22-char-UID>`, e.g.
`Widgets#DWl6nx5eD0Ws5ElP75cfgQ`, `UserActions#iCnZkeZp7US8oQ7YQB15yg`,
`NodesNotShownInESpaceTree#HF__GdRwvEybg686MpM7YA`, and a compound form
`NodesNotShownInESpaceTree#B4kRGvrnOEmQonA8ir4Pyg.#FlowExceptionHandler`.

### Plaintext header
Pipe-delimited ASCII, 36,219 bytes. First fields:
`11.0.415.100|11.55.93.65333|155|Am0mHuuAS0yPh37L4weNBQ|RwMjGVcwcGSBdSaklTLyzA|True|TestApplication|An application to |2026-10-21 11:16:15|J7pB0r6rRF5GhEoPIwOswg|/NRWebFlows.fWtJs57lI0qCTlwkcDoxDA/Nodes...`

OML/model version `11.0.415.100`, platform version `11.55.93.65333`, revision `155`,
then the eSpace UID `Am0mHuuAS0yPh37L4weNBQ` — which **matches `Reference UID` in
Manifest.xml**, confirming the manifest↔oml join key. The header also carries
model-graph paths of the form `/<Collection>.<22-char-UID>/<SubCollection>` and
Newtonsoft-JSON (`$type`/`$id`/`$ref`) presenter state leaking internal namespaces
`OutSystems.MetaModel`, `OutSystems.MetaModel.CompoundKeys.RootCompoundKey`,
`ServiceStudio.Presenter`, `ServiceStudio.Framework`.

**Note the header is where the version triple lives, and it is plaintext and
uncompressed** — so a pipeline can cheaply version-gate every file before attempting
to inflate it.

### Encryption status: none
- Not encrypted. The file is obscure, not protected. Entropy ~6.37 bits/byte;
  the 36 KB header is plain ASCII; the body inflates with a stock raw-deflate call and
  no key. The widespread community belief that only Service Studio can read an OML is
  simply wrong.
- The earlier 0.387 printable ratio is explained by the 36 KB ASCII header plus ASCII
  runs inside the compressed stream — it was never evidence about compression.

## 4. Implications for the pipeline

1. **Tier 0 (free):** `unzip` the `.oap`, parse `Manifest.xml`. Inventory and dependency
   graph with no OutSystems software and no format knowledge.
2. **Tier 1 (solved, ~20 lines):** read the `OML` magic, the uint32 LE header length,
   slice the plaintext header, `zlib.decompressobj(-15)` the remainder, walk the
   93-record directory, split out Fast Infoset fragments. Fully verified above.
3. **Tier 2 (needs a real decoder):** decode Fast Infoset to XML. `strings` on the
   fragments already yields names and values — structure `MasterDetailItem`, client
   action `OfflineDataSync` with `IsAsync` and input `SyncUnit`, client variable
   `LastURL`, default theme, default screen `MainFlow\Screen1`, validation messages —
   but a correct tree needs an FI decoder (no Python stdlib support; .NET has
   `Noemax.FastInfoset`).
4. **Tier 3 (hardest):** expressions are stored as pre-parsed `ParsedExpression` ASTs
   with type-by-key references, so recovering readable expression *text* is the hardest
   target and should be scoped explicitly rather than assumed.

## 5. Confidence labelling

- **Measured / independently re-verified:** `.oap` = plain ZIP and its contents; the ZIP
  comment string; the Manifest.xml text quoted; magic `OML`; header length 36,219 at
  `0x03`; raw-deflate body at 36,226 inflating to 8,185,876 bytes; the 93-fragment
  directory and its exact length reconciliation; the fragment names and sizes tabulated;
  the manifest UID ↔ oml UID match.
- **Reported by the format researcher, consistent with the above but not re-checked by
  the coordinator:** Fast Infoset identification (`E0 00 00 01`, ITU-T X.891); the
  Newtonsoft/presenter-state namespaces; the `ParsedExpression` AST claim; entropy 6.37.
- **Unidentified:** the first 1,492 bytes of the inflated blob.
- **Not tested:** multi-module `.oap`; `.osp`; ODC packaging; round-trip repacking and
  whether `Signature`/`GeneralHash`/`APIHash` must be recomputed to republish;
  cross-version stability of the framing.

## 6. Caveat on generalisation
One near-trivial single-module `CrossDevice` app from one Service Studio build
(`11.0.415.100` / platform `11.55.93.65333`, revision `155`). Framing details may vary
across versions — note that `kelter-antunes/oml-utilities` embeds
`OutSystems.Common.11.0.520.0` and has an `UnsupportedNewerVersion` path, so
version coupling is a real, documented failure mode. Any parser must dispatch on the
header version triple and fail loudly on unknown revisions.
