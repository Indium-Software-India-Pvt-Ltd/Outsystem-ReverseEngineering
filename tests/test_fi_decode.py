"""Tests for the Fast Infoset decoder.

The grammar in fi_decode.py was derived empirically from one real OutSystems
module, so these tests exist mainly to stop a refactor silently reintroducing a
decoding bug. That matters more than usual here: every bug found while building
the decoder produced plausible-looking XML rather than an error.

Assertions are split deliberately:

  * `VERIFIED` in a docstring means the expected value is anchored in real bytes
    whose meaning was established independently - a UID whose length can be
    counted, a sentence that reads continuously, a PNG whose CRC checks out.
  * `CHARACTERISATION` means the test pins current behaviour to catch drift, but
    the value itself is not independently confirmed. Those are honest guards,
    not proof of correctness.
"""

import unittest

import _ctx  # noqa: F401  (sys.path side effect)

import fi_decode as fi


# --------------------------------------------------------------------------- #
# Bit reader
# --------------------------------------------------------------------------- #

class TestBitReader(unittest.TestCase):
    def test_bit_order_is_most_significant_first(self):
        r = fi.BitReader(bytes([0b1011_0010]))
        self.assertEqual([r.bit() for _ in range(8)], [1, 0, 1, 1, 0, 0, 1, 0])

    def test_bits_accumulates_big_endian(self):
        r = fi.BitReader(bytes([0b1011_0010]))
        self.assertEqual(r.bits(4), 0b1011)
        self.assertEqual(r.bits(4), 0b0010)

    def test_peek_does_not_advance(self):
        r = fi.BitReader(bytes([0xAB, 0xCD]))
        self.assertEqual(r.peek_bits(8), 0xAB)
        self.assertEqual(r.pos, 0)
        self.assertEqual(r.octet(), 0xAB)

    def test_octet_refuses_unaligned_read(self):
        r = fi.BitReader(bytes([0xFF, 0xFF]))
        r.bits(3)
        with self.assertRaises(fi.FIError):
            r.octet()

    def test_reading_past_end_raises(self):
        r = fi.BitReader(bytes([0x00]))
        r.bits(8)
        with self.assertRaises(fi.FIError):
            r.bit()

    def test_align_checked_rejects_non_zero_padding(self):
        # A literal qname must start octet-aligned; non-zero pad bits mean the
        # grammar is being misread, so they must fail rather than be skipped.
        r = fi.BitReader(bytes([0b0000_0111]))
        r.bits(5)
        with self.assertRaises(fi.FIError):
            r.align_checked("name")

    def test_align_checked_accepts_zero_padding(self):
        r = fi.BitReader(bytes([0b0000_0000]))
        r.bits(5)
        r.align_checked("name")
        self.assertTrue(r.aligned())


# --------------------------------------------------------------------------- #
# Length forms
# --------------------------------------------------------------------------- #

class TestIdentifyingLength(unittest.TestCase):
    """Literal name lengths. Bit 1 is the literal/index discriminator, so the
    length field starts at bit 2."""

    def test_single_octet_form(self):
        """VERIFIED: 0x0d precedes the 14-character name 'eSpaceFragment'."""
        self.assertEqual(fi.BitReader(bytes([0x0D])).identifying_length(), 14)

    def test_single_octet_boundaries(self):
        self.assertEqual(fi.BitReader(bytes([0x00])).identifying_length(), 1)
        self.assertEqual(fi.BitReader(bytes([0x3F])).identifying_length(), 64)

    def test_two_octet_escape(self):
        """VERIFIED: 0x40 0x01 precedes the 66-character name
        'NRWebWidgets.CustomWidget-OutSystems.Plugin.NRWidgets.AdvancedHtml'.

        Reading this as the one-octet form yields 65 and truncates the name by
        one character, which desynchronises everything after it.
        """
        self.assertEqual(fi.BitReader(bytes([0x40, 0x01])).identifying_length(), 66)

    def test_two_octet_escape_starts_at_65(self):
        self.assertEqual(fi.BitReader(bytes([0x40, 0x00])).identifying_length(), 65)

    def test_index_octet_is_not_a_length(self):
        # Top bit set means "index into the name table"; asking for a length
        # here is a caller bug and must not silently return a huge number.
        with self.assertRaises(fi.FIError):
            fi.BitReader(bytes([0x94])).identifying_length()


class TestNonIdentifyingLength(unittest.TestCase):
    """Attribute-value and character-chunk lengths.

    These share one position-dependent rule. With k bits left in the octet:
        0  + (k-1) bits         -> 1 .. 2^(k-1)
        10 + (k-2) bits + octet -> escape, leading bits are HIGH bits
        11 + (k-2) bits + 4 oct -> next escape up
    """

    @staticmethod
    def _at(hexstr, consumed):
        r = fi.BitReader(bytes.fromhex(hexstr))
        r.bits(consumed)
        return r

    # -- attribute values start with k=4 (4 bits already consumed) ---------- #

    def test_attr_small_form(self):
        """VERIFIED: 0x43 precedes '2285' (4 chars); 0x42 precedes '457' (3);
        0x44 precedes 'Align' (5)."""
        self.assertEqual(self._at("43", 4).nonidentifying_length(), 4)
        self.assertEqual(self._at("42", 4).nonidentifying_length(), 3)
        self.assertEqual(self._at("44", 4).nonidentifying_length(), 5)

    def test_attr_small_form_boundaries(self):
        self.assertEqual(self._at("40", 4).nonidentifying_length(), 1)
        self.assertEqual(self._at("47", 4).nonidentifying_length(), 8)

    def test_attr_one_octet_escape(self):
        """VERIFIED: 0x48 0x0d precedes a 22-character base64url UID
        ('oPAVm_5RKQJYaaLy7uswHA'). 22-char UIDs dominate this format, and this
        pair occurs ~2500 times in the reference module."""
        self.assertEqual(self._at("480d", 4).nonidentifying_length(), 22)
        self.assertEqual(self._at("4804", 4).nonidentifying_length(), 13)
        self.assertEqual(self._at("480a", 4).nonidentifying_length(), 19)
        self.assertEqual(self._at("4835", 4).nonidentifying_length(), 62)

    def test_attr_one_octet_escape_starts_at_9(self):
        # The small form covers 1..8, so the escape necessarily begins at 9.
        self.assertEqual(self._at("4800", 4).nonidentifying_length(), 9)

    def test_attr_four_octet_escape(self):
        """VERIFIED: 0x4c 00 00 01 33 precedes a 572-byte description string.

        The offset of 265 is forced: the one-octet form covers 9..264. It was
        also fitted independently across 201 samples in the reference module.
        """
        self.assertEqual(self._at("4c00000133", 4).nonidentifying_length(), 572)
        self.assertEqual(self._at("4c00000000", 4).nonidentifying_length(), 265)

    def test_attr_escape_leading_bits_are_significant(self):
        """CHARACTERISATION: the bits between the form selector and the octet
        boundary are high bits of the value, not padding.

        They are zero in almost every real fragment, which is exactly why
        treating them as padding went unnoticed until References.finf.
        """
        # 0x4b -> nibble 1011: '10' selector, then high bits 0b11 = 3.
        self.assertEqual(self._at("4b40", 4).nonidentifying_length(), (3 << 8 | 0x40) + 9)

    # -- character chunks start with k=2 (6 bits already consumed) ---------- #

    def test_chunk_one_octet_escape(self):
        """VERIFIED: 0x92 0x0d precedes 'Security Warning' (16 chars); 0x92 0x81
        precedes a 132-byte sentence; 0x92 0x13 precedes 22-char UIDs."""
        self.assertEqual(self._at("920d", 6).nonidentifying_length(), 16)
        self.assertEqual(self._at("920b", 6).nonidentifying_length(), 14)
        self.assertEqual(self._at("9213", 6).nonidentifying_length(), 22)
        self.assertEqual(self._at("9281", 6).nonidentifying_length(), 132)

    def test_chunk_small_form_covers_one_and_two(self):
        # k=2 leaves a single value bit, so the small form spans only 1..2 and
        # the escape begins at 3.
        self.assertEqual(self._at("90", 6).nonidentifying_length(), 1)
        self.assertEqual(self._at("91", 6).nonidentifying_length(), 2)
        self.assertEqual(self._at("9200", 6).nonidentifying_length(), 3)

    def test_same_second_octet_means_different_lengths(self):
        """REGRESSION: the constants are position-dependent.

        Second octet 0x0d means 22 for an attribute value (k=4) but 16 for a
        character chunk (k=2). Reusing one site's constants at the other is the
        single biggest trap in this format - it silently drops the first
        characters of every text chunk rather than raising.
        """
        self.assertEqual(self._at("480d", 4).nonidentifying_length(), 22)
        self.assertEqual(self._at("920d", 6).nonidentifying_length(), 16)


# --------------------------------------------------------------------------- #
# Indices and name slots
# --------------------------------------------------------------------------- #

class TestIndexForms(unittest.TestCase):
    @staticmethod
    def _dec(hexstr, consumed):
        d = fi.FastInfosetDecoder(bytes.fromhex(hexstr))
        d.r.bits(consumed)
        return d

    def test_small_form_at_k6_element_name(self):
        """CHARACTERISATION: 0x1b in element position -> index 28.

        The small form is exercised ~25,000 times in the reference module, so
        its shape is well supported even though this particular value's name
        was not checked by hand.
        """
        self.assertEqual(self._dec("1b", 2).read_index(), 28)

    def test_escape_form_at_k5_character_chunk(self):
        """VERIFIED: 0xb4 0x0e resolves to content index 1047, which lands on a
        real table entry in ReferersData.finf."""
        self.assertEqual(self._dec("b40e", 3).read_index(), 1047)

    def test_index_width_depends_on_bit_position(self):
        """REGRESSION: read_index must derive its field width from the current
        bit position, not take it as a constant.

        The same two bytes mean different things depending on how many bits the
        enclosing item already consumed. Hardcoding 7 available bits is correct
        for an attribute value (starts at bit 1) and wrong for a character
        chunk's value (starts at bit 3).
        """
        at_bit_1 = self._dec("b40e", 1).read_index()
        at_bit_3 = self._dec("b40e", 3).read_index()
        self.assertNotEqual(at_bit_1, at_bit_3)

    def test_too_few_head_bits_raises(self):
        d = self._dec("ff", 6)
        with self.assertRaises(fi.FIError):
            d.read_index()


class TestNameSlots(unittest.TestCase):
    """A prefix / namespace / local-name slot is index-or-literal."""

    @staticmethod
    def _dec(hexstr, table_size=200):
        d = fi.FastInfosetDecoder(bytes.fromhex(hexstr))
        d.v.local_name = [f"n{i}" for i in range(1, table_size + 1)]
        return d

    def test_literal_slot_appends_to_table(self):
        d = fi.FastInfosetDecoder(bytes.fromhex("03") + b"Name")
        self.assertEqual(d.name_or_index(d.v.local_name, "local name"), "Name")
        self.assertEqual(d.v.local_name, ["Name"])

    def test_indexed_slot_one_octet_form(self):
        """REGRESSION: a top-bit-set octet is a table index, not a length.

        0x94 read as a length yields a 5253-byte octet string and overruns the
        fragment; read as an index it is entry 21.
        """
        d = self._dec("94")
        self.assertEqual(d.name_or_index(d.v.local_name, "local name"), "n21")

    def test_indexed_slot_two_octet_form(self):
        """REGRESSION: an index whose first octet starts 0b11 carries a second
        octet.

        0xc0 0x0b is index 76. Reading it as the one-octet form consumes a byte
        too few and then mistakes the following value byte for a value start -
        this was the last failure in References.finf.
        """
        d = self._dec("c00b")
        self.assertEqual(d.name_or_index(d.v.local_name, "local name"), "n76")

    def test_one_octet_form_boundary(self):
        self.assertEqual(self._dec("80").name_or_index(
            fi.FastInfosetDecoder(b"").v.local_name or ["n1"], "local name"), "n1")

    def test_index_out_of_range_raises(self):
        d = self._dec("94", table_size=3)
        with self.assertRaises(fi.FIError):
            d.name_or_index(d.v.local_name, "local name")


# --------------------------------------------------------------------------- #
# Encoding algorithms (embedded binary)
# --------------------------------------------------------------------------- #

class TestEncodingAlgorithm(unittest.TestCase):
    def test_algorithm_id_is_eight_bits_not_an_aligned_octet(self):
        """REGRESSION: the algorithm id is 8 bits read at the current bit
        position, straddling the octet boundary inside a character chunk.

        VERIFIED from three image-bearing fragments: '8c 07 00 00 05 69' means
        algorithm 1 with a 1644-byte payload, and consuming exactly that lands
        the decoder on 'f0 3c 0c TextResources' in all three. Reading the id as
        an aligned octet instead gives a length of 1 and walks into the PNG.
        """
        payload = bytes(range(256)) * 7            # 1792 >= 1644 bytes
        d = fi.FastInfosetDecoder(bytes.fromhex("8c0700000569") + payload)
        d.r.bits(2)                                # the '10' chunk marker
        value = d.read_value(d.v.content, "character chunk")
        self.assertIsInstance(value, fi.Encoded)
        self.assertEqual(value.algorithm, 1)
        self.assertEqual(len(value.data), 1644)
        self.assertEqual(value.data, payload[:1644])

    def test_encoded_payload_counted_in_stats(self):
        d = fi.FastInfosetDecoder(bytes.fromhex("8c0700000569") + bytes(2000))
        d.r.bits(2)
        d.read_value(d.v.content, "character chunk")
        self.assertEqual(d.stats["encoded_payloads"], 1)
        self.assertEqual(d.stats["encoded_bytes"], 1644)


# --------------------------------------------------------------------------- #
# Whole-document golden tests
# --------------------------------------------------------------------------- #

LICENSED_FEATURES = bytes.fromhex(
    "e0000001003c0d655370616365467261676d656e743c0f"
    "4c6963656e7365644665617475726573fff0"
)
UNUSED_DEPENDENCIES = bytes.fromhex(
    "e0000001003c0d655370616365467261676d656e743c11"
    "556e75736564446570656e64656e63696573fff0"
)
ESPACE_CONFIGURATIONS = bytes.fromhex(
    "e0000001003c0d655370616365467261676d656e747c13457370616365436f6e"
    "66696775726174696f6e73780a47656e6572616c48617368480d6f5041566d5f"
    "35524b514a5961614c79377573774841f03c0c546578745265736f7572636573"
    "f03c074d65746164617461ffff"
)


class TestGoldenDocuments(unittest.TestCase):
    """Three real fragments small enough to have been decoded by hand.

    VERIFIED: each byte of these was accounted for manually before the decoder
    existed, so they pin the document framing, terminator packing, literal
    qnames, attributes and the k=4 value escape all at once.
    """

    def test_minimal_document(self):
        root, stats = fi.decode_fragment(LICENSED_FEATURES)
        self.assertEqual(root.name, "eSpaceFragment")
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].name, "LicensedFeatures")
        self.assertEqual(stats["elements"], 2)
        self.assertEqual(stats["attributes"], 0)

    def test_minimal_document_serialises(self):
        root, _ = fi.decode_fragment(LICENSED_FEATURES)
        self.assertEqual(
            fi.to_xml(root, pretty=False),
            "<eSpaceFragment><LicensedFeatures/></eSpaceFragment>",
        )

    def test_name_length_is_read_per_fragment(self):
        root, _ = fi.decode_fragment(UNUSED_DEPENDENCIES)
        self.assertEqual(root.children[0].name, "UnusedDependencies")

    def test_document_with_attribute_and_siblings(self):
        root, stats = fi.decode_fragment(ESPACE_CONFIGURATIONS)
        cfg = root.children[0]
        self.assertEqual(cfg.name, "EspaceConfigurations")
        self.assertEqual(cfg.attrs, [("GeneralHash", "oPAVm_5RKQJYaaLy7uswHA")])
        self.assertEqual([c.name for c in cfg.children],
                         ["TextResources", "Metadata"])
        self.assertEqual(stats["elements"], 4)
        self.assertEqual(stats["attributes"], 1)

    def test_attribute_header_pads_to_the_octet_boundary(self):
        """REGRESSION: an element header is exactly 8 bits but an attribute
        header is 7 and pads.

        Without the pad the attribute name length is read one bit early and the
        decoder dies on an unaligned octet read. The attribute value above is
        the proof it is handled.
        """
        root, _ = fi.decode_fragment(ESPACE_CONFIGURATIONS)
        self.assertEqual(root.children[0].attrs[0][0], "GeneralHash")


class TestFailsLoudly(unittest.TestCase):
    """The decoder must never emit plausible-but-wrong XML.

    Every bug found while building it produced readable output rather than an
    error, so these guard the failure behaviour itself.
    """

    def test_missing_magic(self):
        with self.assertRaises(fi.FIError):
            fi.decode_fragment(b"XML\x01" + LICENSED_FEATURES[4:])

    def test_truncated_fragment(self):
        with self.assertRaises(fi.FIError):
            fi.decode_fragment(LICENSED_FEATURES[:-4])

    def test_trailing_bytes_are_rejected(self):
        # The exact-consumption check is the decoder's main correctness oracle.
        with self.assertRaises(fi.FIError) as ctx:
            fi.decode_fragment(LICENSED_FEATURES + b"\x00\x00")
        self.assertIn("unconsumed", str(ctx.exception))

    def test_optional_document_components_rejected(self):
        # Flags are zero in every observed fragment; a non-zero value means a
        # feature this decoder does not implement.
        data = bytearray(LICENSED_FEATURES)
        data[4] = 0x01
        with self.assertRaises(fi.FIError):
            fi.decode_fragment(bytes(data))

    def test_error_message_locates_the_failure(self):
        with self.assertRaises(fi.FIError) as ctx:
            fi.decode_fragment(b"XML\x01\x00")
        self.assertIn("byte", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
