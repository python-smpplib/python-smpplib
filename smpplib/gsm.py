# -*- coding: utf8 -*-
import binascii
import random
import six

from . import consts
from . import exceptions


# from http://stackoverflow.com/questions/2452861/python-library-for-converting-plain-text-ascii-into-gsm-7-bit-character-set
gsm = (six.u("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>"
             "?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà"))
ext = (six.u("````````````````````^```````````````````{}`````\\````````````[~]`"
             "|````````````````````````````````````€``````````````````````````"))


class EncodeError(ValueError):
    """Raised if text cannot be represented in gsm 7-bit encoding"""


def gsm_encode(plaintext, hex=False):
    """Replace non-GSM ASCII symbols"""
    res = ""
    for c in plaintext:
        idx = gsm.find(c)
        if idx != -1:
            res += chr(idx)
            continue
        idx = ext.find(c)
        if idx != -1:
            res += chr(27) + chr(idx)
            continue
        raise EncodeError()
    return binascii.b2a_hex(res) if hex else res


def make_parts(text):
    """Returns tuple(parts, encoding, esm_class)"""
    try:
        text = gsm_encode(text)
        encoding = consts.SMPP_ENCODING_DEFAULT
        need_split = len(text) > consts.SEVENBIT_SIZE
        partsize = consts.SEVENBIT_MP_SIZE
        encode = six.b
    except EncodeError:
        encoding = consts.SMPP_ENCODING_ISO10646
        need_split = len(text) > consts.UCS2_SIZE
        partsize = consts.UCS2_MP_SIZE
        encode = lambda s: s.encode('utf-16-be')

    esm_class = consts.SMPP_MSGTYPE_DEFAULT

    if need_split:
        esm_class = consts.SMPP_GSMFEAT_UDHI

        starts = tuple(range(0, len(text), partsize))
        if len(starts) > 255:
            raise exceptions.MessageTooLong()

        parts = []
        ipart = 1
        uid = random.randint(0, 255)
        for start in starts:
            parts.append( b''.join((b'\x05\x00\x03', six.int2byte(uid),
                                    six.int2byte(len(starts)), six.int2byte(ipart),
                                    encode(text[start:start + partsize]))) )
            ipart += 1
    else:
        parts = (encode(text),)

    return parts, encoding, esm_class
