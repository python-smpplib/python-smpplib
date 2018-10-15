# -*- coding: utf8 -*-
import random

import six

from smpplib import consts, exceptions


def make_parts(text, encoding=consts.SMPP_ENCODING_DEFAULT):
    """Returns tuple(parts, encoding, esm_class)"""
    try:
        # Try to encode with the user-defined encoding first.
        encode, split_length, part_size = ENCODINGS[encoding]
        encoded_text = encode(text)
    except KeyError:
        raise NotImplementedError('encoding is not supported: %s' % encoding)
    except UnicodeError:
        # Fallback to UCS-2.
        encoding = consts.SMPP_ENCODING_ISO10646
        encode, split_length, part_size = ENCODINGS[encoding]
        encoded_text = encode(text)

    if len(text) > split_length:
        # Split the text into well-formed parts.
        esm_class = consts.SMPP_GSMFEAT_UDHI
        # FIXME: 7-bit encoding has variable-length characters.
        # FIXME: it means that a character may be broken by splitting.
        parts = make_parts_encoded(encoded_text, part_size)
    else:
        # Normal message.
        esm_class = consts.SMPP_MSGTYPE_DEFAULT
        parts = [encoded_text]

    return parts, encoding, esm_class


# Source:
# http://stackoverflow.com/questions/2452861/python-library-for-converting-plain-text-ascii-into-gsm-7-bit-character-set
GSM_CHARACTER_TABLE = (
    u"@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>"
    u"?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà"
    u"````````````````````^```````````````````{}`````\\````````````[~]`"
    u"|````````````````````````````````````€``````````````````````````"
)


def gsm_encode(plaintext):
    """Performs default GSM 7-bit encoding. Beware it's vendor-specific and not recommended for use."""
    try:
        return b''.join(
            six.int2byte(index) if index < 0x80 else b'\x1B' + six.int2byte(index - 0x80)
            for index in map(GSM_CHARACTER_TABLE.index, plaintext)
        )
    except ValueError:
        raise UnicodeError(plaintext)


# Map GSM encoding into a tuple of encode function, maximum single message size and a part size.
# Add new entry here should you need to use another encoding.
ENCODINGS = {
    consts.SMPP_ENCODING_DEFAULT: (gsm_encode, consts.SEVENBIT_LENGTH, consts.SEVENBIT_PART_SIZE),
    consts.SMPP_ENCODING_ISO88591: (lambda text: text.encode('iso-8859-1'), consts.EIGHTBIT_LENGTH, consts.EIGHTBIT_PART_SIZE),
    consts.SMPP_ENCODING_ISO10646: (lambda text: text.encode('utf-16-be'), consts.UCS2_LENGTH, consts.UCS2_PART_SIZE),
}


def make_parts_encoded(encoded_text, part_size):
    """Splits encoded text into SMS parts"""
    chunks = split_sequence(encoded_text, part_size)
    if len(chunks) > 255:
        raise exceptions.MessageTooLong()

    uid = random.randint(0, 255)
    header = b''.join((b'\x05\x00\x03', six.int2byte(uid), six.int2byte(len(chunks))))

    return [b''.join((header, six.int2byte(i), chunk)) for i, chunk in enumerate(chunks, start=1)]


def split_sequence(sequence, part_size):
    """Splits the sequence into equal parts"""
    return [sequence[i:i + part_size] for i in range(0, len(sequence), part_size)]

def make_ucs2_compatible_parts(text):
    """
    This method will make correct partition for latin and cyrillic letters
    :param text: Text to partition
    :return: parts, encoding, esm_class
    """
    text_to_encode = text
    parts = []

    part = b''
    for letter in text_to_encode:
        encoded_letter = letter.encode('utf-16-be')
        if len(part) + len(encoded_letter) < consts.UCS2_MP_SIZE:
            part += encoded_letter
        else:
            parts.append(part)
            part = encoded_letter
    parts.append(part)

    esm_class = consts.SMPP_MSGTYPE_DEFAULT
    if len(parts) > 1:
        esm_class = consts.SMPP_GSMFEAT_UDHI
        uid = six.int2byte(random.randint(0, 255))
        parts = [b''.join((b'\x05\x00\x03',
                           uid,
                           six.int2byte(len(parts)),
                           six.int2byte(i + 1),
                           current_part))
                 for i, current_part in enumerate(parts)]

    return parts, consts.SMPP_ENCODING_ISO10646, esm_class
