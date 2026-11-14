# -*- coding: utf8 -*-

import mock
from pytest import mark, raises

from smpplib import consts, exceptions
from smpplib.gsm import gsm_encode, make_parts, make_parts_encoded


@mark.parametrize('plaintext, encoded_text', [
    (u'@', b'\x00'),
    (u'^', b'\x1B\x14'),
])
def test_gsm_encode(plaintext, encoded_text):
    assert gsm_encode(plaintext) == encoded_text


@mark.parametrize('plaintext', [
    (u'Ая',),
])
def test_gsm_encode_unicode_error(plaintext):
    with raises(UnicodeError):
        gsm_encode(plaintext)


@mark.parametrize('plaintext, encoding, expected_parts, expected_encoding', [
    (u'@', consts.SMPP_ENCODING_DEFAULT, [b'\x00'], consts.SMPP_ENCODING_DEFAULT),
    (u'Ая', consts.SMPP_ENCODING_DEFAULT, [b'\x04\x10\x04O'], consts.SMPP_ENCODING_ISO10646),
    (u'é', consts.SMPP_ENCODING_ISO88591, [b'\xe9'], consts.SMPP_ENCODING_ISO88591),
])
def test_make_parts_single(plaintext, encoding, expected_parts, expected_encoding):
    assert make_parts(plaintext, encoding) == (expected_parts, expected_encoding, consts.SMPP_MSGTYPE_DEFAULT)


@mark.parametrize('plaintext, expected', [
    (u'@' * consts.SEVENBIT_PART_SIZE * 2, [
        b'\x05\x00\x03\x42\x02\x01' + b'\x00' * consts.SEVENBIT_PART_SIZE,
        b'\x05\x00\x03\x42\x02\x02' + b'\x00' * consts.SEVENBIT_PART_SIZE,
    ]),
])
def test_make_parts_multiple(plaintext, expected):
    with mock.patch('random.randint') as randint:
        randint.return_value = 0x42
        assert make_parts(plaintext) == (expected, consts.SMPP_ENCODING_DEFAULT, consts.SMPP_GSMFEAT_UDHI)


@mark.parametrize('encoded_text, part_size, expected', [
    (b'12345', 5, [b'\x05\x00\x03\x42\x01\x0112345']),
    (b'12345', 2, [b'\x05\x00\x03\x42\x03\x0112', b'\x05\x00\x03\x42\x03\x0234', b'\x05\x00\x03\x42\x03\x035']),
])
def test_make_parts_encoded(encoded_text, part_size, expected):
    with mock.patch('random.randint') as randint:
        randint.return_value = 0x42
        assert make_parts_encoded(encoded_text, part_size) == expected


@mark.parametrize('text, expected', [
    (u'Привет мир!\n' * 10, 2),
])
def test_part_number(text, expected):
    parts, _, _ = make_parts(text)
    assert len(parts) == expected


@mark.parametrize('character, encoded', [
    (u'^', b'\x1b\x14'),
    (u'{', b'\x1b\x28'),
    (u'}', b'\x1b\x29'),
    (u'\\', b'\x1b\x2f'),
    (u'[', b'\x1b\x3c'),
    (u'~', b'\x1b\x3d'),
    (u']', b'\x1b\x3e'),
    (u'|', b'\x1b\x40'),
    (u'€', b'\x1b\x65'),
])
@mark.parametrize('use_udhi', [True, False])
def test_extended_character_at_part_boundary(character, encoded, use_udhi):
    text = u'a' * 152 + character + u'b' * 10

    with mock.patch('random.randint', return_value=0x42):
        parts, encoding, esm_class = make_parts(text, use_udhi=use_udhi)

    expected = [b'a' * 152, encoded + b'b' * 10]
    if use_udhi:
        expected = [b'\x05\x00\x03\x42\x02\x01' + expected[0],
                    b'\x05\x00\x03\x42\x02\x02' + expected[1]]

    assert parts == expected
    assert encoding == consts.SMPP_ENCODING_DEFAULT
    assert esm_class == (consts.SMPP_GSMFEAT_UDHI if use_udhi else
                         consts.SMPP_MSGTYPE_DEFAULT)


@mark.parametrize('use_udhi', [True, False])
def test_extended_characters_fill_parts(use_udhi):
    parts, encoding, _ = make_parts(u'^' * 160, use_udhi=use_udhi)
    payloads = [part[6:] if use_udhi else part for part in parts]

    assert payloads == [b'\x1b\x14' * 76, b'\x1b\x14' * 76,
                        b'\x1b\x14' * 8]
    assert encoding == consts.SMPP_ENCODING_DEFAULT


@mark.parametrize('use_udhi', [True, False])
def test_extended_character_part_limit(use_udhi):
    parts, _, _ = make_parts(u'^' * (76 * 255), use_udhi=use_udhi)
    assert len(parts) == 255

    with raises(exceptions.MessageTooLong):
        make_parts(u'^' * (76 * 255 + 1), use_udhi=use_udhi)


@mark.parametrize('use_udhi', [True, False])
def test_binary_escape_at_part_boundary(use_udhi):
    text = u'a' * 133 + u'\x1b' + u'b' * 10
    parts, encoding, _ = make_parts(text, consts.SMPP_ENCODING_ISO88591,
                                    use_udhi=use_udhi)
    payloads = [part[6:] if use_udhi else part for part in parts]

    assert payloads == [b'a' * 133 + b'\x1b', b'b' * 10]
    assert encoding == consts.SMPP_ENCODING_ISO88591


def test_encoded_parts_without_encoding():
    with mock.patch('random.randint', return_value=0x42):
        assert make_parts_encoded(b'a\x1bb', 2) == [
            b'\x05\x00\x03\x42\x02\x01a\x1b',
            b'\x05\x00\x03\x42\x02\x02b',
        ]
