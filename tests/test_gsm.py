# -*- coding: utf8 -*-

import mock
from pytest import mark, raises

from smpplib import consts
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
