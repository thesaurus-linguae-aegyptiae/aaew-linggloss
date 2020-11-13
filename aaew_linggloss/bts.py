from .mapping import FLEXCODES


def resolve_flexcode(flexcode) -> str:
    """ looks up the corresponding glossing encoding for a given flexcode
    number.

    >>> resolve_flexcode(96423)
    'Aux.tw=.stpr.2sgf_(Prep)_Verb'

    >>> resolve_flexcode('10930')
    'SC.pass.gem.impers'

    >>> resolve_flexcode('sdafjh')

    :param flexcode: a BTS flexcode
    :type flexcode: str or int
    :returns: verbalized glossing information
    """
    return FLEXCODES.get(
        str(flexcode)
    )
