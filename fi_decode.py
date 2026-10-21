#!/usr/bin/env python3
"""
Stage 2 Fast Infoset decoder — turn OutSystems .finf fragments into real XML.

Fast Infoset (ITU-T X.891 / ISO-IEC 24824-1) is a bit-oriented binary XML
encoding with dynamic vocabulary tables: a name or value is written literally
the first time and referenced by table index afterwards. That indexing is why
`strings` output is lossy — it sees the first occurrence of a name and nothing
about where it recurs.

This decoder was derived empirically from real OutSystems fragments and is
validated by a hard oracle: it must consume every fragment to the exact final
bit. A wrong grammar desynchronises and fails loudly rather than emitting
plausible-but-wrong XML.

Grammar as measured (bit positions are 1-based within an octet):

  Document   : 32-bit magic E0000001, then 8 bits of optional-component flags
               (all zero in every observed fragment), then children closed by
               a 4-bit terminator.

  Element    : bit1=0, bit2=attributes-present, then bits3-6=1111 for a literal
               qname (bit7 prefix-present, bit8 namespace-present) or an index
               into ELEMENT_NAME.

  Attribute  : bit1=0, then bits2-5=1111 for a literal qname (bit6 prefix,
               bit7 namespace, bit8 zero pad) or an index into ATTRIBUTE_NAME.
               Note the element header lands exactly on the octet boundary but
               the attribute header is one bit short and pads.

  Name slot  : each of prefix / namespace / local-name is index-or-literal.
               Top bit clear -> a literal string, length per `identifying_length`
               below, appended to its table. Top bit set -> an index:
                   10 + 6 bits           -> 1..64
                   11 + 6 bits + octet   -> 65..

  Terminator : 4 bits of 1111, nibble-packed. `ff` is two terminators; `f0` is
               one terminator plus 4 bits of padding back to the boundary.

  Lengths and indices are POSITION-DEPENDENT. Given k bits left in the current
  octet, both use the shape:
       0  + (k-1) bits          -> the small range
       10 + (k-2) bits + octet  -> an escape, those bits being the HIGH bits
       11 + (k-2) bits + ...    -> the next escape up
  so the same logical field has different constants at different call sites: an
  attribute value starts with k=4 and a character chunk's value with k=2. This
  is the single biggest trap in the format - reusing one site's constants at
  another silently truncates every value rather than failing.

  Literal name lengths use the same shape starting at bit 2, because bit 1 is
  the literal/index discriminator: 0 0xxxxxx -> 1..64, 0 10xxxxx + octet ->
  65..8256, 0 11xxxxx + four octets -> above that.

  Binary payloads (embedded images) arrive as a character chunk with encoding
  format 11: an 8-BIT algorithm id read at the current bit position, then a
  length under the rule above, then raw octets. They are preserved as bytes and
  emitted as <fi-encoded algorithm=".." octets="..">base64</fi-encoded>.

Status messages go to stderr; XML goes to stdout or to files.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

FI_MAGIC = b"\xe0\x00\x00\x01"

# Indexed name slots are 1-based. Settled semantically, not by guesswork: with
# base 0 a Boolean literal node decodes as Parameter="False", with base 1 as
# Value="False". Only the latter is a real OutSystems attribute.
NAME_INDEX_BASE = 1

# Extra octets carried by the third (11-prefixed) index form.
#
# UNRESOLVED. This form is exercised exactly twice in the 8.19 MB reference
# module, at References.finf (k=7) and ReferersData.finf (k=5), and the two
# sites disagree: References only synchronises with one extra octet, while
# ReferersData only synchronises with none - its value would otherwise be
# 127049, which cannot index a 4810-entry table. So either the form carries a
# discriminator not identified here, or one of the two sites is the symptom of
# an earlier, subtler desynchronisation. Settling it needs a reference encoder
# or a second sample application. The value below decodes 92 of 93 fragments;
# the remaining one fails loudly rather than emitting wrong XML.
THIRD_FORM_EXTRA_OCTETS = 1


class FIError(Exception):
    """The byte stream does not match the Fast Infoset grammar."""

    def __init__(self, msg: str, reader: "BitReader | None" = None):
        if reader is not None:
            msg = f"{msg} (at {reader.where()})"
        super().__init__(msg)


# --------------------------------------------------------------------------- #
# Bit-level reader
# --------------------------------------------------------------------------- #

class BitReader:
    __slots__ = ("data", "pos")

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0  # absolute bit position

    # -- position helpers -------------------------------------------------- #
    @property
    def nbits(self) -> int:
        return len(self.data) * 8

    def remaining(self) -> int:
        return self.nbits - self.pos

    def aligned(self) -> bool:
        return self.pos % 8 == 0

    def align(self) -> None:
        if self.pos % 8:
            self.pos += 8 - (self.pos % 8)

    def align_checked(self, reader_what: str) -> None:
        """Align to the next octet, asserting the skipped bits are all zero.

        Names are octet strings, so a literal qname must begin octet-aligned.
        An element header lands on the boundary exactly; an attribute header is
        one bit short and pads. Checking the pad bits are zero turns a wrong
        grammar into a loud failure instead of a silent misread.
        """
        if self.pos % 8 == 0:
            return
        n = 8 - (self.pos % 8)
        pad = self.bits(n)
        if pad != 0:
            raise FIError(
                f"non-zero padding {pad:#x} in {n} bit(s) before {reader_what}", self
            )

    def where(self) -> str:
        byte, bit = divmod(self.pos, 8)
        lo = max(0, byte - 4)
        ctx = self.data[lo:byte + 6].hex(" ")
        return f"byte {byte} bit {bit}, context {ctx}"

    # -- primitives -------------------------------------------------------- #
    def bit(self) -> int:
        if self.pos >= self.nbits:
            raise FIError("read past end of fragment", self)
        byte, off = divmod(self.pos, 8)
        self.pos += 1
        return (self.data[byte] >> (7 - off)) & 1

    def bits(self, n: int) -> int:
        v = 0
        for _ in range(n):
            v = (v << 1) | self.bit()
        return v

    def peek_bits(self, n: int) -> int:
        save = self.pos
        try:
            if self.remaining() < n:
                raise FIError("read past end of fragment", self)
            return self.bits(n)
        finally:
            self.pos = save

    def octet(self) -> int:
        if not self.aligned():
            raise FIError("octet read while not octet-aligned", self)
        return self.bits(8)

    def octets(self, n: int) -> bytes:
        if not self.aligned():
            raise FIError("octet-string read while not octet-aligned", self)
        byte = self.pos // 8
        if byte + n > len(self.data):
            raise FIError(f"octet-string of {n} overruns fragment", self)
        self.pos += n * 8
        return self.data[byte:byte + n]

    # -- FI length forms --------------------------------------------------- #
    def identifying_length(self) -> int:
        """Length of a literal identifying string (a name).

        Bit 1 of the octet is the literal/index discriminator and has already
        been shown to be 0 by the caller, so the length field starts at bit 2:

            0 0xxxxxx                -> length 1..64, value = len-1
            0 10xxxxx + octet        -> length 65..8256,  value = len-65
            0 11xxxxx + four octets  -> length 8257..,    value = len-8257

        Reading the second form as the first is what silently truncates long
        names such as NRWebWidgets.CustomWidget-OutSystems.Plugin...AdvancedHtml
        by one character and desynchronises everything after it.
        """
        first = self.octet()
        if first & 0x80:
            raise FIError(
                f"identifying_length called on an index octet {first:#04x}", self
            )
        if not (first & 0x40):                       # 0 0xxxxxx
            return (first & 0x3F) + 1
        if not (first & 0x20):                       # 0 10xxxxx + octet
            return ((first & 0x1F) << 8 | self.octet()) + 65
        return int.from_bytes(self.octets(4), "big") + 8257

    def nonidentifying_length(self) -> int:
        """Length of a non-identifying string (attribute value, text chunk).

        One rule covers every call site. Let k be the number of bits left in
        the current octet when the field starts:

            0  + (k-1) bits   -> length 1 .. 2^(k-1), value = len-1
            10 + one octet    -> length = octet + 2^(k-1) + 1
            11 + four octets  -> length = value + 2^(k-1) + 257

        After the 1- or 2-bit selector the rest of the octet is zero padding.

        This is why the constants differ per call site and must not be
        hardcoded: an attribute value starts with k=4 (small form 1..8, then
        +9, then +265), while a character chunk starts with k=2 (small form
        1..2, then +3, then +259). Fitting the attribute constants and reusing
        them for text chunks loses the first character of every chunk.
        """
        k = 8 - (self.pos % 8)
        if k == 0:
            k = 8
        small_max = 1 << (k - 1)

        if self.bit() == 0:                       # 0 + (k-1) bits
            return self.bits(k - 1) + 1

        four_octet = self.bit()                   # 10 -> one, 11 -> four
        # Whatever is left of the octet holds the HIGH bits of the value. These
        # are zero in the overwhelming majority of real fragments, which makes
        # it easy to mistake them for padding; References.finf carries a 0b11
        # there and desynchronises the moment they are discarded.
        high = self.bits(k - 2) if k > 2 else 0
        base = small_max + 1
        if not four_octet:
            return (high << 8 | self.octet()) + base
        return (high << 32 | int.from_bytes(self.octets(4), "big")) + base + 256


# --------------------------------------------------------------------------- #
# Vocabulary
# --------------------------------------------------------------------------- #

class Vocabulary:
    """FI dynamic tables. All indices in the encoding are 1-based."""

    def __init__(self) -> None:
        self.prefix: list[str] = []
        self.namespace: list[str] = []
        self.local_name: list[str] = []
        self.element_name: list[tuple[str | None, str | None, str]] = []
        self.attribute_name: list[tuple[str | None, str | None, str]] = []
        self.attribute_value: list[str] = []
        self.content: list[str] = []

    @staticmethod
    def get(table: list, index: int, what: str, reader: BitReader) -> object:
        if not 1 <= index <= len(table):
            raise FIError(
                f"{what} index {index} out of range (table holds {len(table)})", reader
            )
        return table[index - 1]


# --------------------------------------------------------------------------- #
# Decoder
# --------------------------------------------------------------------------- #

class Encoded:
    """Octets carried by an FI encoding algorithm rather than as UTF-8 text.

    OutSystems uses this for embedded binary resources (images and the like).
    The bytes are preserved verbatim; the decoder does not pretend to know the
    algorithm's semantics, only its identifier and length.
    """

    __slots__ = ("algorithm", "data")

    def __init__(self, algorithm: int, data: bytes):
        self.algorithm = algorithm
        self.data = data


class Element:
    __slots__ = ("name", "attrs", "children")

    def __init__(self, name: str):
        self.name = name
        self.attrs: list[tuple[str, str]] = []
        self.children: list["Element | str"] = []


class FastInfosetDecoder:
    def __init__(self, data: bytes, strict: bool = True):
        self.r = BitReader(data)
        self.v = Vocabulary()
        self.strict = strict
        self.stats = {
            "elements": 0,
            "attributes": 0,
            "text_nodes": 0,
            "literal_element_names": 0,
            "indexed_element_names": 0,
            "literal_attr_names": 0,
            "indexed_attr_names": 0,
            "indexed_values": 0,
            "comments": 0,
            "pis": 0,
            "encoded_payloads": 0,
            "encoded_bytes": 0,
        }

    # -- document ---------------------------------------------------------- #
    def decode(self) -> Element:
        r = self.r
        if r.octets(4) != FI_MAGIC:
            raise FIError("missing Fast Infoset magic E0000001", r)

        flags = r.octet()
        if flags:
            # additional data / initial vocabulary / notations / etc.
            raise FIError(
                f"optional document components present (flags {flags:#04x}); "
                "not implemented",
                r,
            )

        root: Element | None = None
        while True:
            if r.remaining() < 4:
                break
            kind = r.peek_bits(4)
            if kind == 0b1111:
                r.bits(4)
                break
            if kind >> 3 == 0:                       # element
                el = self.read_element()
                if root is None:
                    root = el
                elif self.strict:
                    raise FIError("more than one document element", r)
                continue
            if kind >> 2 == 0b10:                    # characters at document level
                self.read_characters()
                continue
            self.read_other(kind)

        if root is None:
            raise FIError("no document element found", r)
        self.finish()
        return root

    def finish(self) -> None:
        """Consume trailing padding and assert the fragment ended exactly."""
        r = self.r
        if not r.aligned():
            pad = r.bits(8 - (r.pos % 8))
            if pad != 0:
                raise FIError(f"non-zero trailing padding {pad:#x}", r)
        if r.remaining() != 0:
            raise FIError(
                f"{r.remaining() // 8} byte(s) left unconsumed after the document", r
            )

    # -- names ------------------------------------------------------------- #
    def name_or_index(self, table: list[str], what: str) -> str:
        """A name slot inside a literal qualified name.

        The slot is index-or-literal, discriminated by the top bit of the first
        octet. Top bit clear: a literal string whose length-1 is in the low 7
        bits, which is then appended to `table`. Top bit set: a reference to an
        entry already in `table`. Missing this distinction is what makes a
        naive decoder read a table index as a 5 KB string length.
        """
        r = self.r
        first = r.peek_bits(8)
        if not (first & 0x80):
            text = r.octets(r.identifying_length()).decode("utf-8")
            table.append(text)
            return text

        # Indexed slot. Two forms, distinguished by the second bit:
        #     10 + 6 bits            -> index 1..64
        #     11 + 6 bits + octet    -> index 65..
        # Treating the second form as the first reads one octet too few and
        # then mistakes the following value byte for the start of a value.
        r.octet()
        low = first & 0x3F
        if not (first & 0x40):
            idx = low + NAME_INDEX_BASE
        else:
            idx = (low << 8 | r.octet()) + 64 + NAME_INDEX_BASE
        return Vocabulary.get(table, idx, what, r)  # type: ignore[return-value]

    def read_qname(self, prefix_flag: int, ns_flag: int, table: list) -> str:
        prefix = ns = None
        if prefix_flag:
            prefix = self.name_or_index(self.v.prefix, "prefix")
        if ns_flag:
            ns = self.name_or_index(self.v.namespace, "namespace")
        local = self.name_or_index(self.v.local_name, "local name")
        table.append((prefix, ns, local))
        return f"{prefix}:{local}" if prefix else local

    @staticmethod
    def qname_str(entry: tuple[str | None, str | None, str]) -> str:
        prefix, _ns, local = entry
        return f"{prefix}:{local}" if prefix else local

    def read_index(self) -> int:
        """Index value, read from wherever the stream currently sits.

        The field width depends on how many bits are left in the current octet
        (call it k), and the leading bits select one of three widths:

            0  + (k-1) bits          -> 1 .. 2^(k-1)
            10 + (k-2) bits + octet  -> 2^(k-2)+1 .. 2^(k-2)+2^(k+6)
            11 + (k-2) bits + octet  -> the range above that

        Both escape forms keep their leading bits as the HIGH bits of the
        value. The offsets below are the ones the data actually supports; note
        the first two ranges overlap slightly, so they are not derivable from
        the widths alone and must not be "tidied up" - doing so reassigns every
        escaped index and silently resolves names to the wrong table entry.

        Passing k in as a constant is wrong for the same reason it is wrong for
        lengths: an attribute value starts at bit 1, a character chunk's value
        at bit 3.
        """
        r = self.r
        k = 8 - (r.pos % 8)
        if k == 0:
            k = 8
        if k < 3:
            raise FIError(f"index field with only {k} bit(s) of head", r)

        head = r.bits(k)
        top = 1 << (k - 1)
        if not (head & top):                      # 0 + (k-1) bits
            return (head & (top - 1)) + 1

        mid = top >> 1
        high = head & (mid - 1)                   # the (k-2) low bits of head
        value = high << 8 | r.octet()
        if not (head & mid):                      # 10 ...
            return value + mid + 1
        for _ in range(THIRD_FORM_EXTRA_OCTETS):  # 11 ...
            value = value << 8 | r.octet()
        return value + mid + 1 + (1 << (k + 6))

    # -- items ------------------------------------------------------------- #
    def read_element(self) -> Element:
        r = self.r
        if r.bit() != 0:
            raise FIError("read_element called off an element boundary", r)
        has_attrs = r.bit()

        disc = r.peek_bits(4)
        if disc == 0b1111:
            r.bits(4)
            prefix_flag, ns_flag = r.bit(), r.bit()
            # [0][attrs][1111][prefix][ns] is exactly 8 bits, so this is a no-op
            # for elements; kept for symmetry and to assert the invariant.
            r.align_checked("element name")
            name = self.read_qname(prefix_flag, ns_flag, self.v.element_name)
            self.stats["literal_element_names"] += 1
        else:
            idx = self.read_index()
            entry = Vocabulary.get(self.v.element_name, idx, "element name", r)
            name = self.qname_str(entry)  # type: ignore[arg-type]
            self.stats["indexed_element_names"] += 1

        el = Element(name)
        self.stats["elements"] += 1

        if has_attrs:
            while True:
                self.skip_padding_before_item()
                if r.peek_bits(4) == 0b1111:
                    r.bits(4)
                    break
                self.read_attribute(el)
            self.pad_after_terminator()

        while True:
            if r.remaining() < 4:
                raise FIError(f"fragment ends inside <{name}>", r)
            kind = r.peek_bits(4)
            if kind == 0b1111:
                r.bits(4)
                break
            if kind >> 3 == 0:
                el.children.append(self.read_element())
            elif kind >> 2 == 0b10:
                el.children.append(self.read_characters())
            else:
                self.read_other(kind)
        self.pad_after_terminator()
        return el

    def read_attribute(self, el: Element) -> None:
        r = self.r
        if r.bit() != 0:
            raise FIError("attribute must start with a 0 bit", r)
        disc = r.peek_bits(4)
        if disc == 0b1111:
            r.bits(4)
            prefix_flag, ns_flag = r.bit(), r.bit()
            # [0][1111][prefix][ns] is 7 bits; one zero pad bit follows.
            r.align_checked("attribute name")
            name = self.read_qname(prefix_flag, ns_flag, self.v.attribute_name)
            self.stats["literal_attr_names"] += 1
        else:
            idx = self.read_index()
            entry = Vocabulary.get(self.v.attribute_name, idx, "attribute name", r)
            name = self.qname_str(entry)  # type: ignore[arg-type]
            self.stats["indexed_attr_names"] += 1

        value = self.read_value(self.v.attribute_value, "attribute value")
        if isinstance(value, Encoded):
            # An attribute cannot hold raw octets; surface it as base64 and
            # flag it rather than silently mangling the bytes into text.
            value = base64.b64encode(value.data).decode("ascii")
            name = f"{name}.base64"
        el.attrs.append((name, value))
        self.stats["attributes"] += 1

    def read_value(self, table: list[str], what: str):
        """Non-identifying string: literal (optionally table-added) or an index."""
        r = self.r
        if r.bit():                                   # index into the table
            idx = self.read_index()
            self.stats["indexed_values"] += 1
            return Vocabulary.get(table, idx, what, r)  # type: ignore[return-value]
        add_to_table = r.bit()
        fmt = r.bits(2)
        if fmt == 0b11:
            # Encoding algorithm. The identifier is 8 *bits* read at the current
            # bit position, not an octet-aligned byte: inside a character chunk
            # it straddles the octet boundary. The length then follows under the
            # same position-dependent rule as any other non-identifying string.
            # Reading the id as an aligned octet instead yields a length of 1 and
            # walks straight into the payload - which for OutSystems is a PNG.
            algorithm = r.bits(8)
            length = r.nonidentifying_length()
            self.stats["encoded_payloads"] += 1
            self.stats["encoded_bytes"] += length
            return Encoded(algorithm, r.octets(length))
        if fmt != 0b00:
            raise FIError(
                f"{what} uses encoding format {fmt:#b} (only UTF-8 literals and "
                "encoding algorithms are implemented)",
                r,
            )
        n = r.nonidentifying_length()
        raw = r.octets(n)
        text = raw.decode("utf-8", errors="replace")
        if add_to_table:
            table.append(text)
        return text

    def read_characters(self):
        r = self.r
        if r.bits(2) != 0b10:
            raise FIError("character chunk must start with bits 10", r)
        text = self.read_value(self.v.content, "character chunk")
        self.stats["text_nodes"] += 1
        return text

    def read_other(self, kind: int) -> None:
        raise FIError(
            f"unsupported content item, leading bits {kind:#06b} "
            "(comment / PI / DTD / unexpanded entity)",
            self.r,
        )

    # -- alignment --------------------------------------------------------- #
    def skip_padding_before_item(self) -> None:
        """An attribute list item is octet-aligned; absorb 4 bits of padding."""
        r = self.r
        if r.pos % 8 == 4:
            if r.peek_bits(4) == 0:
                r.bits(4)

    def pad_after_terminator(self) -> None:
        """Terminators are nibble-packed; realign only when padding follows.

        `ff` is two terminators, so do not blindly align: peek first and only
        consume an all-zero nibble.
        """
        r = self.r
        if r.pos % 8 == 4 and r.remaining() >= 4:
            if r.peek_bits(4) == 0:
                r.bits(4)


# --------------------------------------------------------------------------- #
# Serialization
# --------------------------------------------------------------------------- #

def to_xml(el: Element, indent: int = 0, pretty: bool = True) -> str:
    pad = "  " * indent if pretty else ""
    nl = "\n" if pretty else ""
    attrs = "".join(f" {k}={quoteattr(v)}" for k, v in el.attrs)
    if not el.children:
        return f"{pad}<{el.name}{attrs}/>{nl}"
    only_text = all(isinstance(c, str) for c in el.children)
    if only_text:
        text = escape("".join(c for c in el.children))  # type: ignore[misc]
        return f"{pad}<{el.name}{attrs}>{text}</{el.name}>{nl}"
    out = [f"{pad}<{el.name}{attrs}>{nl}"]
    for child in el.children:
        if isinstance(child, str):
            if child.strip():
                out.append(f"{'  ' * (indent + 1) if pretty else ''}{escape(child)}{nl}")
        elif isinstance(child, Encoded):
            ipad = "  " * (indent + 1) if pretty else ""
            b64 = base64.b64encode(child.data).decode("ascii")
            out.append(
                f'{ipad}<fi-encoded algorithm="{child.algorithm}" '
                f'octets="{len(child.data)}">{b64}</fi-encoded>{nl}'
            )
        else:
            out.append(to_xml(child, indent + 1, pretty))
    out.append(f"{pad}</{el.name}>{nl}")
    return "".join(out)


def decode_fragment(data: bytes, strict: bool = True) -> tuple[Element, dict]:
    dec = FastInfosetDecoder(data, strict=strict)
    root = dec.decode()
    return root, dec.stats


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="fi_decode.py",
        description="Decode OutSystems Fast Infoset fragments (.finf) to XML.",
    )
    ap.add_argument("inputs", nargs="+", type=Path, help=".finf files or directories")
    ap.add_argument("-o", "--out", type=Path, help="write .xml files here")
    ap.add_argument("--no-pretty", action="store_true", help="single-line output")
    ap.add_argument("--summary", action="store_true",
                    help="only report per-fragment status, no XML")
    ap.add_argument("--stop-on-error", action="store_true")
    args = ap.parse_args(argv)

    files: list[Path] = []
    for p in args.inputs:
        if p.is_dir():
            files.extend(sorted(p.glob("*.finf")))
        else:
            files.append(p)
    if not files:
        print("error: no .finf inputs found", file=sys.stderr)
        return 2

    ok = fail = 0
    totals: dict[str, int] = {}
    failures: list[tuple[str, str]] = []

    for f in files:
        try:
            root, stats = decode_fragment(f.read_bytes())
        except FIError as exc:
            fail += 1
            failures.append((f.name, str(exc)))
            print(f"FAIL  {f.name}: {exc}", file=sys.stderr)
            if args.stop_on_error:
                return 1
            continue
        except Exception as exc:  # unexpected: still attributable to this file
            fail += 1
            failures.append((f.name, f"{type(exc).__name__}: {exc}"))
            print(f"FAIL  {f.name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            if args.stop_on_error:
                return 1
            continue

        ok += 1
        for k, v in stats.items():
            totals[k] = totals.get(k, 0) + v
        print(
            f"ok    {f.name}: {stats['elements']} elements, "
            f"{stats['attributes']} attrs, {stats['text_nodes']} text",
            file=sys.stderr,
        )

        if args.summary:
            continue
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + to_xml(
            root, pretty=not args.no_pretty
        )
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / (f.stem + ".xml")).write_text(xml, encoding="utf-8")
        else:
            sys.stdout.write(xml)

    print(f"\n[{ok} ok, {fail} failed]", file=sys.stderr)
    if totals:
        print("totals: " + json.dumps(totals, sort_keys=True), file=sys.stderr)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
