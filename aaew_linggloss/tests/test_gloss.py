import pytest

from .. import (
    bts,
    computeLingGlossing,
    resolve_flexcode,
)


def test_flexcode_resource():
    assert bts.FLEXCODES != None


def test_flexcode():
    assert resolve_flexcode('-10168') == 'SC.pass.spec.2du'


def test_gloss():
    g = computeLingGlossing(
        70060, '125581',
        {
            'type': 'substantive',
            'subtype': 'substantive_masc'
        }
    )
    assert g == 'N.m:sg:stc'
