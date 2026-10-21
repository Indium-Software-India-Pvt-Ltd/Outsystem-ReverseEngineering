#!/usr/bin/env python3
"""
Stage 1 OML extractor — unpack OutSystems .oap/.oml down to raw model fragments.

Scope (deliberately bounded):
    .oap  -> ZIP container, Manifest.xml, one .oml per module
    .oml  -> plaintext header + raw-DEFLATE body
    body  -> preamble, fragment directory, N concatenated Fast Infoset documents

What this does NOT do: decode Fast Infoset into an XML tree. That is Stage 2 and
needs a real FI decoder (Python has none in stdlib; .NET has Noemax.FastInfoset).
Expressions are stored as pre-parsed ParsedExpression ASTs with type-by-key
references, so readable expression *text* is harder still and out of scope here.

Verified format (measured on a real O11 package, byte-exact):

    offset 0x00   3 bytes    ASCII magic b"OML"
    offset 0x03   4 bytes    uint32 LE header length H
    offset 0x07   H bytes    plaintext '|'-delimited ASCII header
    offset 7+H    remainder  raw DEFLATE (wbits=-15, no zlib/gzip wrapper)

Inflated blob:

    [0 .. D)          preamble (contains a uint32 LE fragment count + flag bytes)
    [D .. D+L)        fragment directory: N records of
                          uint32 LE nameLen | name (ASCII) | uint32 LE contentLen
    [D+L .. EOF)      N concatenated Fast Infoset docs, each starting E0 00 00 01

Correctness is established structurally, not by trusting constants. The directory
is located by scanning for the longest self-consistent record run whose declared
content lengths sum to exactly (len(blob) - directory_end) AND all of whose bodies
begin with the Fast Infoset magic. That reconciliation is unambiguous: on the
reference file it lands on EOF with zero slack. The 1,492 / 5,524 offsets observed
on one file are therefore never hardcoded.

Status messages go to stderr; the JSON summary goes to stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
import zlib
from pathlib import Path

OML_MAGIC = b"OML"
FI_MAGIC = b"\xe0\x00\x00\x01"
HEADER_LEN_OFFSET = 3
HEADER_TEXT_OFFSET = 7

# How far into the inflated blob to look for the directory. The reference file
# puts it at 1,492; this is generous headroom without being unbounded.
MAX_DIR_SCAN = 65536
MAX_NAME_LEN = 512

# (oml_model_version, platform_version, revision) triples this parser has been
# checked against end to end. Unknown builds warn by default rather than abort:
# the structural reconciliation above is a far stronger guarantee than a version
# allowlist, and hard-failing every new Service Studio build would make the tool
# useless on first contact. Use --strict-version where an abort is preferred.
VERIFIED_BUILDS = {
    ("11.0.415.100", "11.55.93.65333", "155"),
}

# Header field order, positional. Only the first three are structurally reliable;
# later text fields (notably Description) can in principle contain '|'.
HEADER_FIELDS = [
    "oml_model_version",
    "platform_version",
    "revision",
    "espace_uid",
    "secondary_uid",
    "flag",
    "module_name",
    "description",
    "last_modified",
    "tail_uid",
]

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._#+-]")
_PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{%d,}")


class OmlFormatError(Exception):
    """The input does not match the verified OML layout."""


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #

def parse_header(data: bytes) -> tuple[str, int, dict]:
    """Validate the magic, read the length-prefixed plaintext header.

    Returns (header_text, body_offset, parsed_fields).
    """
    if len(data) < HEADER_TEXT_OFFSET:
        raise OmlFormatError(f"file is {len(data)} bytes; too short to hold an OML header")
    if data[:3] != OML_MAGIC:
        raise OmlFormatError(f"bad magic {data[:3]!r}, expected {OML_MAGIC!r}")

    header_len = struct.unpack_from("<I", data, HEADER_LEN_OFFSET)[0]
    body_offset = HEADER_TEXT_OFFSET + header_len
    if body_offset > len(data):
        raise OmlFormatError(
            f"declared header length {header_len} overruns the file "
            f"({body_offset} > {len(data)})"
        )

    raw = data[HEADER_TEXT_OFFSET:body_offset]
    header_text = raw.decode("utf-8", errors="replace")

    parts = header_text.split("|")
    fields: dict[str, object] = {}
    for i, name in enumerate(HEADER_FIELDS):
        fields[name] = parts[i] if i < len(parts) else None
    fields["header_length"] = header_len
    fields["body_offset"] = body_offset
    fields["field_count"] = len(parts)
    return header_text, body_offset, fields


def check_version(fields: dict, strict: bool) -> bool:
    triple = (
        str(fields.get("oml_model_version")),
        str(fields.get("platform_version")),
        str(fields.get("revision")),
    )
    known = triple in VERIFIED_BUILDS
    if not known:
        msg = (
            f"  !! unverified build {triple[0]} / {triple[1]} / rev {triple[2]} "
            f"(tested: {sorted(VERIFIED_BUILDS)})"
        )
        if strict:
            raise OmlFormatError(msg.strip() + " — refusing under --strict-version")
        log(msg)
        log("     proceeding; the structural checks below are authoritative")
    return known


# --------------------------------------------------------------------------- #
# Body
# --------------------------------------------------------------------------- #

def inflate_body(data: bytes, body_offset: int) -> bytes:
    """Inflate the raw-DEFLATE body (no zlib/gzip wrapper, hence wbits=-15)."""
    try:
        blob = zlib.decompressobj(-15).decompress(data[body_offset:])
    except zlib.error as exc:
        raise OmlFormatError(f"raw DEFLATE failed at offset {body_offset}: {exc}") from exc
    if not blob:
        raise OmlFormatError(f"raw DEFLATE at offset {body_offset} produced no output")
    return blob


def _try_directory(blob: bytes, start: int) -> tuple[int, list[tuple[str, int]], int] | None:
    """Parse a directory at `start`, returning the longest self-consistent run.

    Self-consistent means: directory_end + sum(content lengths) == len(blob).
    Returns (directory_end, records, total) or None.
    """
    n = len(blob)
    cur = start
    records: list[tuple[str, int]] = []
    total = 0
    best: tuple[int, list[tuple[str, int]], int] | None = None

    while cur + 4 <= n:
        name_len = struct.unpack_from("<I", blob, cur)[0]
        if not 0 < name_len <= MAX_NAME_LEN:
            break
        name_start = cur + 4
        name_end = name_start + name_len
        if name_end + 4 > n:
            break
        raw_name = blob[name_start:name_end]
        if any(b < 0x20 or b > 0x7E for b in raw_name):
            break
        content_len = struct.unpack_from("<I", blob, name_end)[0]
        if content_len > n:
            break

        cur = name_end + 4
        records.append((raw_name.decode("ascii"), content_len))
        total += content_len
        if cur + total == n:
            best = (cur, list(records), total)

    return best


def _bodies_are_fast_infoset(blob: bytes, dir_end: int, records) -> tuple[int, int]:
    ok = 0
    offset = dir_end
    for _, length in records:
        if blob[offset:offset + 4] == FI_MAGIC:
            ok += 1
        offset += length
    return ok, len(records)


def locate_directory(blob: bytes) -> dict:
    """Find the fragment directory structurally. Never trusts a fixed offset."""
    limit = min(MAX_DIR_SCAN, len(blob))
    best: dict | None = None

    for start in range(limit):
        found = _try_directory(blob, start)
        if not found:
            continue
        dir_end, records, total = found
        fi_ok, fi_total = _bodies_are_fast_infoset(blob, dir_end, records)
        cand = {
            "directory_offset": start,
            "directory_end": dir_end,
            "records": records,
            "content_total": total,
            "fi_ok": fi_ok,
            "fi_total": fi_total,
        }
        # Prefer an all-Fast-Infoset solution, then the one with most records.
        key = (fi_ok == fi_total, len(records))
        if best is None or key > (best["fi_ok"] == best["fi_total"], len(best["records"])):
            best = cand

    if best is None:
        raise OmlFormatError(
            "no self-consistent fragment directory found in the first "
            f"{limit} bytes of the inflated blob"
        )
    return best


def find_preamble_count(blob: bytes, dir_offset: int, n_fragments: int) -> dict | None:
    """Locate the uint32 LE fragment count in the preamble.

    On the reference file the blob opens at offset 0 with `5d 00 00 00` (= 93),
    the exact fragment count, which independently corroborates the directory
    record count parsed further down. The N bytes immediately following are
    *unidentified*: measured at 77 distinct values across 93 bytes, they are
    high-entropy and therefore NOT flag or type tags. One byte per fragment of
    high-entropy data is consistent with a per-fragment hash or checksum, but
    that is unconfirmed and this parser does not rely on it.
    """
    for off in range(0, max(0, dir_offset - 4)):
        if struct.unpack_from("<I", blob, off)[0] != n_fragments:
            continue
        trailing = blob[off + 4:off + 4 + n_fragments]
        if len(trailing) != n_fragments:
            continue
        return {
            "offset": off,
            "count": n_fragments,
            # purpose unknown; high entropy, one byte per fragment
            "trailing_block_hex": trailing.hex(),
            "trailing_block_distinct_bytes": len(set(trailing)),
            "trailing_block_note": "unidentified; high entropy, not flag/type tags",
        }
    return None


# --------------------------------------------------------------------------- #
# Output helpers
# --------------------------------------------------------------------------- #

def safe_name(name: str, limit: int = 120) -> str:
    """Filesystem-safe fragment filename, collision-resistant."""
    cleaned = _SAFE_CHARS.sub("_", name)
    if len(cleaned) <= limit:
        return cleaned
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:10]
    return f"{cleaned[:limit - 11]}_{digest}"


def extract_strings(body: bytes, min_len: int) -> list[str]:
    """Printable runs, order-preserving and deduplicated.

    Crude, but it already surfaces action names, structures, variables, screen
    names, themes and validation messages without any FI decoder.
    """
    pattern = re.compile(rb"[\x20-\x7e]{%d,}" % min_len)
    seen: set[str] = set()
    out: list[str] = []
    for match in pattern.findall(body):
        text = match.decode("ascii")
        if text not in seen:
            seen.add(text)
            out.append(text)
    return out


# --------------------------------------------------------------------------- #
# Per-module processing
# --------------------------------------------------------------------------- #

def process_oml(
    data: bytes,
    label: str,
    out_dir: Path | None,
    args: argparse.Namespace,
) -> dict:
    log(f"[oml] {label}  ({len(data):,} bytes)")

    header_text, body_offset, fields = parse_header(data)
    log(
        f"  header: {fields['header_length']:,} bytes plaintext, "
        f"body at {body_offset:,}"
    )
    log(
        f"  module: {fields.get('module_name')!r}  "
        f"oml={fields.get('oml_model_version')} "
        f"platform={fields.get('platform_version')} "
        f"rev={fields.get('revision')}"
    )
    version_known = check_version(fields, args.strict_version)

    blob = inflate_body(data, body_offset)
    ratio = len(blob) / len(data) if data else 0
    log(f"  inflated: {len(blob):,} bytes (raw DEFLATE, {ratio:.2f}x)")

    layout = locate_directory(blob)
    records = layout["records"]
    n = len(records)
    log(
        f"  directory: {n} fragments at offset {layout['directory_offset']:,}"
        f" .. {layout['directory_end']:,}"
    )
    reconciled = layout["directory_end"] + layout["content_total"] == len(blob)
    log(
        f"  reconciliation: {layout['directory_end']:,} + {layout['content_total']:,}"
        f" = {layout['directory_end'] + layout['content_total']:,}"
        f" vs {len(blob):,}  -> {'EXACT' if reconciled else 'MISMATCH'}"
    )
    log(f"  fast infoset: {layout['fi_ok']}/{layout['fi_total']} bodies carry {FI_MAGIC.hex()}")

    preamble = find_preamble_count(blob, layout["directory_offset"], n)
    if preamble:
        log(
            f"  preamble: fragment count {n} corroborated at offset "
            f"{preamble['offset']} (+{n} unidentified bytes, "
            f"{preamble['trailing_block_distinct_bytes']} distinct)"
        )
    else:
        log("  preamble: no corroborating fragment count found (not fatal)")

    # Slice fragments.
    fragments = []
    offset = layout["directory_end"]
    for name, length in records:
        body = blob[offset:offset + length]
        frag = {
            "name": name,
            "offset": offset,
            "length": length,
            "fast_infoset": body[:4] == FI_MAGIC,
            "sha256": sha256(body),
        }
        if out_dir is not None:
            frag_dir = out_dir / "fragments"
            frag_dir.mkdir(parents=True, exist_ok=True)
            path = frag_dir / f"{safe_name(name)}.finf"
            path.write_bytes(body)
            frag["path"] = str(path.relative_to(out_dir))

            if args.strings:
                str_dir = out_dir / "strings"
                str_dir.mkdir(parents=True, exist_ok=True)
                lines = extract_strings(body, args.min_string)
                spath = str_dir / f"{safe_name(name)}.txt"
                spath.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                frag["strings_path"] = str(spath.relative_to(out_dir))
                frag["strings_count"] = len(lines)
        fragments.append(frag)
        offset += length

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "header.txt").write_text(header_text, encoding="utf-8")
        if args.keep_inflated:
            (out_dir / "inflated.bin").write_bytes(blob)
        log(f"  wrote {len(fragments)} fragments -> {out_dir}")

    biggest = sorted(fragments, key=lambda f: -f["length"])[:5]
    for f in biggest:
        pct = 100.0 * f["length"] / len(blob)
        log(f"    {f['length']:>10,}  {pct:5.1f}%  {f['name']}")

    return {
        "label": label,
        "oml_bytes": len(data),
        "oml_sha256": sha256(data),
        "header": fields,
        "version_verified": version_known,
        "inflated_bytes": len(blob),
        "compression_ratio": round(ratio, 4),
        "directory_offset": layout["directory_offset"],
        "directory_end": layout["directory_end"],
        "fragment_count": n,
        "content_total": layout["content_total"],
        "reconciled_exactly": reconciled,
        "fast_infoset_ok": layout["fi_ok"],
        "preamble_count": preamble,
        "fragments": fragments,
    }


# --------------------------------------------------------------------------- #
# Container handling
# --------------------------------------------------------------------------- #

def process_oap(path: Path, out_root: Path | None, args: argparse.Namespace) -> dict:
    log(f"[oap] {path.name}")
    result: dict = {"source": str(path), "kind": "oap", "modules": []}

    with zipfile.ZipFile(path) as zf:
        # The "The Solution Pack Manifest" fingerprint lives on the Manifest.xml
        # *entry*, not on the archive comment, so check both.
        archive_comment = zf.comment.decode("utf-8", errors="replace")
        entry_comments = {
            i.filename: i.comment.decode("utf-8", errors="replace")
            for i in zf.infolist()
            if i.comment
        }
        result["zip_comment"] = archive_comment
        result["zip_entry_comments"] = entry_comments
        if archive_comment:
            log(f"  zip comment: {archive_comment!r}")
        for fname, c in entry_comments.items():
            log(f"  zip comment on {fname}: {c!r}")
        fingerprint = "Solution Pack Manifest"
        if fingerprint in archive_comment or any(
            fingerprint in c for c in entry_comments.values()
        ):
            result["solution_pack_fingerprint"] = True
            log("  -> matches the OutSystems solution-pack fingerprint")
        else:
            result["solution_pack_fingerprint"] = False

        names = zf.namelist()
        manifest_name = next((n for n in names if n.lower().endswith("manifest.xml")), None)
        if manifest_name:
            raw = zf.read(manifest_name)
            result["manifest"] = summarize_manifest(raw)
            if out_root is not None:
                out_root.mkdir(parents=True, exist_ok=True)
                (out_root / "Manifest.xml").write_bytes(raw)
            log(f"  manifest: {manifest_name} ({len(raw):,} bytes)")
            m = result["manifest"]
            log(
                f"    schema={m.get('schema')} hub={m.get('hub_server_version')} "
                f"is_application_pack={m.get('is_application_pack')}"
            )
            for app in m.get("applications", []):
                log(f"    app: {app.get('Name')!r} kind={app.get('ApplicationKind')}")
            shown = set()
            for ref in m.get("references", []):
                key = (ref.get("Kind"), ref.get("UID"))
                if key in shown:
                    continue
                shown.add(key)
                log(f"    ref: {ref.get('Kind')} {ref.get('Name')!r}")
            dup = m.get("reference_element_count", 0) - m.get("distinct_reference_count", 0)
            if dup > 0:
                log(f"    ({dup} duplicate Reference element(s) collapsed)")
        else:
            log("  !! no Manifest.xml in archive")

        oml_names = [n for n in names if n.lower().endswith(".oml")]
        if not oml_names:
            raise OmlFormatError("archive contains no .oml module")
        log(f"  modules: {len(oml_names)}")

        for name in sorted(oml_names):
            stem = Path(name).stem
            out_dir = (out_root / "modules" / safe_name(stem)) if out_root else None
            result["modules"].append(
                process_oml(zf.read(name), f"{path.name}:{name}", out_dir, args)
            )

    return result


def summarize_manifest(raw: bytes) -> dict:
    """Pull the high-value attributes out of Manifest.xml.

    Free structure, no OutSystems software and no format knowledge required:
    module inventory, the eSpace reference graph, app kind, versions, UIDs.
    """
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return {"parse_error": str(exc)}

    out: dict = {
        "bytes": len(raw),
        "schema": root.get("Schema"),
        "hub_server_version": root.get("HubServerVersion"),
        "last_upgrade_version": root.get("LastUpgradeVersion"),
        # the .oap vs .osp discriminator
        "is_application_pack": root.get("IsApplicationPack"),
        "uid": root.get("UID"),
        "creation": root.get("Creation"),
        "solutions": [],
        "applications": [],
        "references": [],
    }

    for sol in root.iter("Solution"):
        out["solutions"].append(
            {k: sol.get(k) for k in ("Name", "UID", "Description", "Creation", "IsTransient")}
        )
    seen_refs = set()
    for ref in root.iter("Reference"):
        rec = {k: ref.get(k) for k in ("Kind", "Name", "UID", "Description")}
        out["references"].append(rec)
        seen_refs.add((rec["Kind"], rec["UID"]))
    # The reference graph is what matters; the raw element list can repeat the
    # same (Kind, UID) pair, so expose both the raw count and the distinct set.
    out["reference_element_count"] = len(out["references"])
    out["distinct_reference_count"] = len(seen_refs)
    for app in root.iter("Application"):
        out["applications"].append(
            {
                k: app.get(k)
                for k in (
                    "Name", "UID", "Description", "ApplicationKind",
                    "FrontOfficeEspaceName", "BackOfficeEspaceName",
                    "PrimaryColor", "APIHash", "ContentHash",
                    "OriginEnvironmentCode", "TemplateKey", "OutdatedReferences",
                )
            }
        )
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="oml_extract.py",
        description="Unpack an OutSystems .oap/.oml to raw model fragments (Stage 1).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s 'Test Application.oap' -o out\n"
            "  %(prog)s app.oap --verify-only\n"
            "  %(prog)s mod.oml -o out --strings --min-string 8\n"
        ),
    )
    ap.add_argument("input", type=Path, help=".oap package or bare .oml module")
    ap.add_argument("-o", "--out", type=Path, help="output directory (omit to only inspect)")
    ap.add_argument("--verify-only", action="store_true",
                    help="parse and validate, write nothing")
    ap.add_argument("--strings", action="store_true",
                    help="also dump printable runs per fragment")
    ap.add_argument("--min-string", type=int, default=6,
                    help="minimum run length for --strings (default: 6)")
    ap.add_argument("--keep-inflated", action="store_true",
                    help="also write the full inflated blob")
    ap.add_argument("--strict-version", action="store_true",
                    help="abort on a build not in VERIFIED_BUILDS")
    ap.add_argument("--quiet", action="store_true", help="suppress stderr progress")
    args = ap.parse_args(argv)

    if args.quiet:
        global log
        log = lambda _msg: None  # noqa: E731

    if not args.input.is_file():
        log(f"error: not a file: {args.input}")
        return 2

    out_root = None if args.verify_only else args.out
    if out_root is None and not args.verify_only:
        log("note: no --out given; inspecting only (nothing will be written)")

    data = args.input.read_bytes()
    try:
        if data[:3] == OML_MAGIC:
            out_dir = out_root
            result = {
                "source": str(args.input),
                "kind": "oml",
                "modules": [process_oml(data, args.input.name, out_dir, args)],
            }
        elif zipfile.is_zipfile(args.input):
            result = process_oap(args.input, out_root, args)
        else:
            log(f"error: {args.input.name} is neither a ZIP container nor an OML file")
            return 2
    except OmlFormatError as exc:
        log(f"error: {exc}")
        return 1

    ok = all(m["reconciled_exactly"] for m in result["modules"])
    result["all_modules_reconciled"] = ok

    if out_root is not None:
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "index.json").write_text(
            json.dumps(result, indent=2, sort_keys=False), encoding="utf-8"
        )
        log(f"[done] index -> {out_root / 'index.json'}")

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
