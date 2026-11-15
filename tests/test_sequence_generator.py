# -*- coding: utf8 -*-

import mock
from pytest import mark, raises
import random

from smpplib.client import SimpleSequenceGenerator

MIN_SEQUENCE = 0x00000001
MAX_SEQUENCE = 0x7FFFFFFF


def test_creation():
    seq_generator = SimpleSequenceGenerator()
    assert MIN_SEQUENCE == seq_generator.sequence

    starting_sequence = random.randint(MIN_SEQUENCE + 1, MIN_SEQUENCE + 101)
    seq_generator = SimpleSequenceGenerator(starting_sequence)
    assert starting_sequence == seq_generator.sequence

    seq_generator = SimpleSequenceGenerator(MAX_SEQUENCE)
    assert MAX_SEQUENCE == seq_generator.sequence

    seq_generator = SimpleSequenceGenerator(MIN_SEQUENCE-1)
    assert MIN_SEQUENCE == seq_generator.sequence

    seq_generator = SimpleSequenceGenerator(MAX_SEQUENCE+1)
    assert MIN_SEQUENCE == seq_generator.sequence