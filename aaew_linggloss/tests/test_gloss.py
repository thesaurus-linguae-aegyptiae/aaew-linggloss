import pytest

from .. import (
    computeLingGlossing,
)


def test_gloss():
    g = computeLingGlossing(
        70060, '125581',
        {
            'type': 'substantive',
            'subtype': 'substantive_masc'
        }
    )
    assert g == 'N.m:sg:stc'
