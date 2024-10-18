from .bts import resolve_flexcode
from .mapping import (
    lingGlossFromLemmaIDDict,
    dictPOSGlossings,
    dictSubPOSGlossings,
    dictPOSGlossingsDefault,
    dictSubPOSGlossingsDefault,
)


def lingGlossFromLemmaID(lemmaID):
    return lingGlossFromLemmaIDDict.get(lemmaID)


def stateFromSuffix (flexcode):
    stateFlex = flexcode % 10 # letzte Ziffer isolieren
    if stateFlex == 0: state = '' # sta, stc or unknown
    else: state = ':stpr' # stpr
    return state


def lingGlossFromPOS(pos, sub_pos):
    if sub_pos != '':
        lingGloss = dictSubPOSGlossings.get(sub_pos)
        if lingGloss:
            return lingGloss
    if pos != '':
        lingGloss = dictPOSGlossings.get(pos)
        if lingGloss != '':
            return lingGloss
    return ''


def defaultFlexFromPOS(pos, sub_pos):
    if sub_pos != '':
        lingGloss = dictSubPOSGlossingsDefault.get(sub_pos)
        if lingGloss:
            return lingGloss
    if pos != '':
        lingGloss = dictPOSGlossingsDefault.get(pos)
        if lingGloss:
            return lingGloss
    return ''


def stemType (sub_pos):
    if     sub_pos == 'verb_3-inf' \
        or sub_pos == 'verb_4-inf' \
        or sub_pos == 'verb_5-inf' \
        or sub_pos == 'verb_caus_3-inf' \
        or sub_pos == 'verb_caus_4-inf' \
        or sub_pos == 'verb_irr':
        return 'inf'
    elif   sub_pos == 'verb_2-gem' \
        or sub_pos == 'verb_3-gem' \
        or sub_pos == 'verb_caus_2-gem' \
        or sub_pos == 'verb_caus_3-gem':
        return 'gem'
    elif   sub_pos == 'verb_2-lit' \
        or sub_pos == 'verb_3-lit' \
        or sub_pos == 'verb_4-lit' \
        or sub_pos == 'verb_5-lit' \
        or sub_pos == 'verb_6-lit' \
        or sub_pos == 'verb_caus_2-lit' \
        or sub_pos == 'verb_caus_3-lit' \
        or sub_pos == 'verb_caus_4-lit' \
        or sub_pos == 'verb_caus_5-lit':
        return 'strong'
    return ''


def computeLingGlossing(flexcode: int, lemmaID: str, pos_subpos: dict):
    """ Apply Leipzig Glossing Rules to Part of Speech and flexion information of a lemma occurrence.
    :param flexcode: BTS flexcode
    :param lemmaID: BTS lemma ID
    :param pos_subpos: BTS part of speech type/subtype; python dictionary with ``type`` and optional ``subtype`` key
    """
    logFile = None # kein Error Log ausgeben
    pos = ''
    sub_pos =''

    if pos_subpos:
        posParts = pos_subpos
        pos = posParts.get('type')
        if len(posParts) > 1:
            sub_pos = posParts.get('subtype')

    # ling. Glossierung aus LemmaID (Pronomina, u.a)
    glossing = lingGlossFromLemmaID(lemmaID)
    if glossing:
        return glossing

    # ling. Glossierung aus flexcode
    glossing = ''
    try:
        flexcode = int(flexcode)
    except ValueError:
        if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid flexcode [no number]: '+flexcode)
        return '(invalid code)'

    if flexcode >= 0:
        algSign = 1
    else:
        algSign = 0
        flexcode = abs(flexcode)

    flex = flexcode % 100000 #Negationsstelle x00000 abschneiden

    # Status-Codes
    if (flexcode >= 0) and (flexcode <= 9):
        glossing = lingGlossFromPOS(pos, sub_pos)
        #if flexcode == 0: glossing += '(flex: unedited)'
        #elif flexcode == 1: glossing += '(flex: ?)'
        #elif flexcode == 2: glossing += '(flex: ?)'
        #elif flexcode == 3: glossing += '(flex: not specified)'
        #elif flexcode == 4: glossing += '(flex: unclear)'
        #elif flexcode == 5: glossing += '(flex: problematic)'
        #elif flexcode == 9: glossing += '(flex: to be reviewed)'
        if flexcode == 3: # only iff sentence is morphologically tagged, cannot be made sure at the moment
            glossing = defaultFlexFromPOS(pos, sub_pos)
        if glossing == '':
            if flexcode == 0: glossing = '(unedited)'
            elif flexcode == 1: glossing = '(?)'
            elif flexcode == 2: glossing = '(?)'
            elif flexcode == 3: glossing = '—'
            elif flexcode == 4: glossing = '(unclear)'
            elif flexcode == 5: glossing = '(problematic)'
            elif flexcode == 9: glossing = '(to be reviewed)'

    # Suffixkonjugation
    elif ((flex // 10000) == 1) or (((flex // 1000) >= 82) and ((flex // 1000) <= 87)):
        glossing = 'V\\tam'
        flex = flex % 10000 # auf 4 Stellen beschneiden, SK-Info weg
        #if (flex // 1000) == 1: # präf.SK
        #    glossing = 'tam:'+glossing
        flex = flex % 1000 # auf 3 Stellen beschneiden, aux.-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)

        #SK-Formen
        flex = flex // 10 # letzte Stelle beschneiden
        skForm = ''
        if   flex ==  0: # 1x00x, "SK" (unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified suffix conjugation flexcode (form, xxx00x): '+str(flexcode))
        elif flex ==  2: skForm = '.act' # 10020, "SK.akt.kzl"
        elif flex ==  4: skForm = '.pass' # 10040, "SK.pass.kzl"
        elif flex == 10:
            skForm = '.act' # 10100, "SK.akt.gem"
            if stemType(sub_pos) == 'inf': # jrr
                glossing = 'V~ipfv'
        elif flex == 12:
            skForm = '.pass' # 10120, "SK.pass.gem=redupl"
            if stemType(sub_pos) == 'strong' \
                or stemType(sub_pos) == 'inf': # sDmm, nDrr; https://wikis.hu-berlin.de/ancientegyptian/%C2%A780
                glossing = 'V~post'
        elif flex == 14: skForm = '.act' # 10140, "SK.akt.spez"
        elif flex == 16: skForm = '.pass' # 10160, "SK.pass.spez"
        elif flex == 17: skForm = '-pass' # 10170, "SK.tw-pass.spez"
        elif flex == 18: skForm = '.act' # 10180, "SK.w-.akt.kzl"
        elif flex == 20: skForm = '.act' # 10200, "Sk.w-.akt.kurz", ##obsolete
        elif flex == 22: skForm = '.act' # 10220, "Sk.w-.akt.gem"
        elif flex == 24: skForm = '.pass' # 10240, "SK.w-.pass.kzl"
        elif flex == 28: skForm = '-pass' # 10280, "SK.w-.tw-pass.kzl"
        elif flex == 30: skForm = '-pass' # 10300, "SK.w-.tw-pass.kurz", ##obsolete
        elif flex == 32: skForm = '-pass' # 10320, "SK.tw-pass.kzl"
        elif flex == 36:
            skForm = '-pass' # 10360, "SK.tw-pass.gem"
            if stemType(sub_pos) == 'inf': # jrr.tw
                glossing = 'V~ipfv'
        elif flex == 38: skForm = '.act-ant' # 10380, "SK.n-.akt.kzl"
        elif flex == 40: skForm = '.act-ant' # 10400, "SK.n-.akt.kurz", ##obsolete
        elif flex == 42: skForm = '.act-ant' # 10420, "SK.n-.akt.gem"
        elif flex == 44: skForm = '-ant-pass' # 10440, "SK.n-.tw-pass.kzl"
        elif flex == 48: skForm = '-ant-pass' # 10480, "SK.n-.tw-pass.gem"
        elif flex == 50: skForm = '.act-cnsv' # 10500, "SK.jn-.akt.kzl"
        elif flex == 54: skForm = '.act-cnsv' # 10540, "SK.jn-.akt.gem"
        elif flex == 56: skForm = '-cnsv-pass' # 10560, "SK.jn-.tw-pass.kzl"
        elif flex == 57: skForm = '-cnsv-pass' # 10570 , "SK.jn-.tw-pass.kzl.unpersönl."
        elif flex == 60: skForm = '.act-oblv' # 10600, "SK.ḫr-.akt.kzl"
        elif flex == 61: skForm = '.act' # 10610, "ḫr SK.akt.kzl"
        elif flex == 64: skForm = '.act-oblv' # 10640, "SK.ḫr-.akt.gem"
        elif flex == 65: skForm = '.act' # 10650, "ḫr SK akt.gem"
        elif flex == 66: skForm = '-oblv-pass' # 10660, "SK.ḫr-.tw-pass.kzl"
        elif flex == 67: skForm = '-pass' # 10670, "ḫr SK-tw.pass.kzl"
        elif flex == 70: skForm = '-oblv-pass' # 10700, "SK.ḫr-.tw-pass.gem"
        elif flex == 71: skForm = '-pass' # 10710, "ḫr SK-tw.pass.gem"
        elif flex == 72: skForm = '.act-post' # 10720, "SK.kꜣ-.akt.kzl"
        elif flex == 73: skForm = '.act' # 10730, "kꜣ SK.akt.kzl"
        elif flex == 76: skForm = '.act-post' # 10760, "SK.kꜣ-.akt.gem"
        elif flex == 77: skForm = '.act' # 10770, "kꜣ SK. akt.gem. "
        elif flex == 78: skForm = '-post-pass' # 10780, "SK.kꜣ-.tw-pass.kzl"
        elif flex == 79: skForm = '-pass' # 10790, "kꜣ SK.-tw-pass.kzl."
        elif flex == 82: skForm = '-post-pass' # 10820, "SK.kꜣ-.tw-pass.gem"
        elif flex == 83: skForm = '-pass' # 10830, "k3 SK.-tw-pass.gem"
        elif flex == 84: skForm = '.act-compl' # 10840, "SK.t-.akt.kzl."
        elif flex == 85: skForm = '.act-compl' # 10850, "SK.t-.akt.gem"
        elif flex == 86: skForm = '.pass-compl' # 10860, "SK.t-.pass.kzl"
        elif flex == 87: skForm = '.pass-compl' # 10870, "SK.t-.pass.gem"
        elif flex == 90: skForm = '.act' # 10900, "SK.akt.kzl.unpersönl."
        elif flex == 91: skForm = '.pass' # 10910, "SK.pass.kzl.unpersönl."
        elif flex == 92:
            skForm = '.act' # 10920, "SK.akt.gem.unpersönl."
            if stemType(sub_pos) == 'inf': # jrr
                glossing = 'V~ipfv'
        elif flex == 93:
            skForm = '.pass' # 10930, "SK.pass.gem.unpersönl."
            if stemType(sub_pos) == 'strong' \
                or stemType(sub_pos) == 'inf': # sDmm, nDrr; https://wikis.hu-berlin.de/ancientegyptian/%C2%A780
                glossing = 'V~post'
        elif flex == 80: skForm = '.act-ant' # 10800, "SK.n-akt.kzl.unpersönl."
        elif flex == 81: skForm = '-ant-pass' # 10810, "SK.n-tw.pass.kzl.unpersönl. "
        elif flex == 94: skForm = '.pass' # 10940, "SK.unpersönl.w-pass."
        elif flex == 95: skForm = '-pass' # 10950, "SK.tw-pass.kzl.unpersönl."
        elif flex == 96: skForm = '-pass' # 10960, "SK.tw-pass.gem.unpersönl."
        elif flex == 19: skForm = '-pass' # 10190 , "SK.tw-pass.spez.unpersönl."
        elif flex == 97: skForm = '.act' # 10970 , "SK.akt.spez.unpersönl."
        elif flex == 98: skForm = '.pass' # 10980 , "SK.pass.spez.unpersönl."
        elif flex == 99: skForm = '.act-compl' # 10990 , "SK.t-akt.kzl.unpersönl."
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid suffix conjugation flexcode (form, pattern xxxXXx): '+str(flexcode))
        glossing += skForm + state

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif (pos == 'adjective' and str(sub_pos) == 'nan'):
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Resultative
    elif (flex // 10000) == 2:
        glossing = 'V\\res'
        flex = flex % 10000 # auf 4 Stellen beschneiden, PsP-Info weg
        #if (flex // 1000) == 1: # präf.PsP
        #    glossing = 'tam:'+glossing
        if (flex // 1000) > 7: # ungültig
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid resultative flexcode (pattern x2[0-7]xxx): '+str(flexcode))

        flex = flex % 1000 # auf 3 Stellen beschneiden, Stamm- & einige aux-Info weg
        flex = flex // 10 # letzte Stelle abschneiden, weitere aux-Info weg

        form = ''
        if   flex ==  0: # 2x00x, "psp" (unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified resultative form (ending, pattern x2x00x): '+str(flexcode))
        elif flex ==  1: form = '-1sg' # 20010, "psp.sg1"
        elif flex ==  2: form = '-2sg.m' # 20020, "psp.sg2m"
        elif flex ==  3: form = '-2sg.f' # 20030, "psp.sg2f"
        elif flex ==  4: form = '-3sg.m' # 20040, "psp.sg3m"
        elif flex == 34: form = '-3sg' # 20040, "psp.sg3"
        elif flex ==  5: form = '-3sg.f' # 20050, "psp.sg3f"
        elif flex ==  6: form = '-1pl' # 20060, "psp.pl1"
        elif flex ==  7: form = '-2pl' # 20070, "psp.pl2"
        elif flex ==  8: form = '-3pl.m' # 20080, "psp.pl3m"
        elif flex == 38: form = '-3pl' # 20080, "psp.pl3"
        elif flex ==  9: form = '-3pl.f' # 20090, "psp.pl3f"
        elif flex == 10: form = '-2du' # 20100, "psp.du2"
        elif flex == 11: form = '-3du.m' # 20110, "psp.du3m"
        elif flex == 31: form = '-3du' # 20110, "psp.du3"
        elif flex == 12: form = '-3du.f' # 20120, "psp.du3f"
        elif flex == 13: form = '-1du' # 20130, "psp.du1"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid resultative flexcode (ending, pattern x2x[1-13/31/34/38]x): '+str(flexcode))
        glossing += form

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined' \
            or (pos == 'adjective' and str(sub_pos) == 'nan'):
                pass # ok
        elif (pos == 'epitheton_title' and str(sub_pos) != 'title') \
            or (pos == 'adverb' and str(sub_pos) == 'nan'):
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Partizip
    elif (flex // 10000) == 3:
        glossing = 'V\\ptcp'
        flex = flex % 10000 # auf 4 Stellen beschneiden, PsP-Info weg

        if (flex // 1000) == 1: # gem.Partizip
            if stemType(sub_pos) == 'inf':
                glossing = 'V~ptcp.distr'
        #elif (flex // 1000) == 2: # präf.Partizip
        #    if str(sub_pos) == 'verb_2-lit': # j.rx.w, https://wikis.hu-berlin.de/ancientegyptian/%C2%A797
        #        glossing = 'V\\ptcp.distr' # wegen nägy. nicht immer korrekt
        elif (flex // 1000) > 2: # ungültig
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid participle flexcode (pattern x3[0-2]xxx): '+str(flexcode))
        flex = flex % 1000 # auf 3 Stellen beschneiden, Stamm-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        ptcpForm = ''
        if   flex ==  0: # 3x00x, "partz" (unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified participle flexcode (genus verbi/number/gender, pattern x3x00x): '+str(flexcode))
        elif flex ==  1: ptcpForm = '.act.m.sg' # 30010, "partz.akt.sgm"
        elif flex ==  2: ptcpForm = '.act.f.sg' # 30020, "partz.akt.sgf"
        elif flex == 32: ptcpForm = '.act.f' # 30320, "partz.akt.sg"
        elif flex ==  3: ptcpForm = '.act.m.pl' # 30030, "partz.akt.plm"
        elif flex ==  4: ptcpForm = '.act.f.pl' # 30040, "partz.akt.plf"
        elif flex ==  5: ptcpForm = '.act.m.du' # 30050, "partz.akt.dum"
        elif flex ==  6: ptcpForm = '.act.f.du' # 30060, "partz.akt.duf"
        elif flex ==  7: ptcpForm = '.pass.m.sg' # 30070, "partz.pass.sgm"
        elif flex ==  8: ptcpForm = '.pass.f.sg' # 30080, "partz.pass.sgf"
        elif flex == 38: ptcpForm = '.pass.f' # 30380, "partz.pass.sg"
        elif flex ==  9: ptcpForm = '.pass.m.pl' # 30090, "partz.pass.plm"
        elif flex == 10: ptcpForm = '.pass.f.pl' # 30100, "partz.pass.plf"
        elif flex == 11: ptcpForm = '.pass.m.du' # 30110, "partz.pass.dum"
        elif flex == 12: ptcpForm = '.pass.f.du' # 30120, "partz.pass.duf"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid participle flexcode (genus verbi/number/gender, pattern x3x[1-12/32/38]x): '+str(flexcode))
        glossing += ptcpForm + state

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined' :
                pass # ok
        elif (pos == 'adjective' and str(sub_pos) == 'nan') \
            or pos == 'substantive' \
            or pos == 'entity_name'\
            or pos == 'epitheton_title':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Relativform
    elif (flex // 10000) == 4:
        glossing = 'V\\rel'
        flex = flex % 10000 # auf 4 Stellen beschneiden, Relf.-Info weg

        stem = ''
        if (flex // 1000) == 1: # gem.Partizip
            if stemType(sub_pos) == 'inf':
                stem = 'redupl'
        #elif (flex // 1000) == 2: # präf.
        #    glossing = 'tam:'+glossing
        elif (flex // 1000) > 2: # ungültig
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid participle flexcode (pattern x4[0-2]xxx): '+str(flexcode))
        flex = flex % 1000 # auf 3 Stellen beschneiden, Stamm-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stellen abschneiden, state-Info weg

        relForm = ''
        tam = ''
        if   flex ==  0: # 4x00x, "rel" (unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified relafive form flexcode (number/gender/tempus, pattern x4x00x): '+str(flexcode))
        elif flex ==  1:
            relForm = '.m.sg-ant' # 40010, "rel.f.n-.sgm" ### ipfv-Kombi nicht als Warnung abgefangen
            tam = 'ant'
        elif flex == 31:
            relForm = '.m-ant' # 40310, "rel.f.n-.m"
            tam = 'ant'
        elif flex ==  2:
            relForm = '.f.sg-ant' # 40020, "rel.f.n-.sgf"
            tam = 'ant'
        elif flex == 32:
            relForm = '.f-ant' # 40320, "rel.f.n-.sg"
            tam = 'ant'
        elif flex ==  3:
            relForm = '.m.pl-ant' # 40030, "rel.f n-.plm"
            tam = 'ant'
        elif flex ==  4:
            relForm = '.f.pl-ant' # 40040, "rel.f.n-.plf"
            tam = 'ant'
        elif flex ==  5:
            relForm = '.m.du-ant' # 40050, "rel.f.n-.dum"
            tam = 'ant'
        elif flex ==  6:
            relForm = '.f.du-ant' # 40060, "rel.f.n-.duf"
            tam = 'ant'
        elif flex ==  7: relForm = '.m.sg' # 40070, "rel.f.sgm"
        elif flex ==  8: relForm = '.f.sg' # 40080, "rel.f.sgf"
        elif flex == 38: relForm = '.f' # 40080, "rel.f.f"
        elif flex ==  9: relForm = '.m.pl' # 40090, "rel.f.plm"
        elif flex == 10: relForm = '.f.pl' # 40100, "rel.f.plf"
        elif flex == 11: relForm = '.m.du' # 40110, "rel.f.dum"
        elif flex == 12: relForm = '.f.du' # 40120, "rel.f.duf"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid relafive form flexcode (number/gender/tempus, pattern x4x[1-12/31/32/38]x): '+str(flexcode))

        if stem == 'redupl':
            if tam != 'ant':
                glossing = 'V~rel.ipfv'
            else:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Anterior relative form with reduplicating stem ('+str(sub_pos)+')<>'+glossing)

        glossing += relForm + state

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined' :
                pass # ok
        elif (pos == 'adjective' and str(sub_pos) == 'nan') \
            or pos == 'substantive' \
            or pos == 'entity_name'\
            or pos == 'epitheton_title' :
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Imperativ
    elif (flex // 10000) == 5:
        glossing = 'V\\imp'
        flex = flex % 10000 # auf 4 Stellen beschneiden, Imp.-Info weg
        #if (flex // 1000) == 1: # präf.
        #    glossing = 'tam:'+glossing
        if (flex // 1000) > 2: # ungültig
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid imperative flexcode (pattern 5[0-2]xxx): '+str(flexcode))
        flex = flex % 1000 # auf 3 Stellen beschneiden, Stamm-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stellen abschneiden, state-Info weg

        form = ''
        if flex == 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified imperative flexcode (pattern 5x0xx): '+str(flexcode))
        elif flex == 1: form = '.sg' # 50010, "imp.sg"
        elif flex == 2: form = '.pl' # 50020, "imp.pl"
        elif flex == 3: form = '.du' # 50030, "imp.du"
        elif flex == 4: form = '' # 50040, "jmj.tw=" ENG §357
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid imperative flexcode (pattern 5x[1-4]xx): '+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        if     pos == 'verb'  \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif (pos == 'particle' and str(sub_pos) != 'particle_enclitic') \
            or pos == 'interjection':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Nominale Verbalformen
    elif (flex // 1000) == 60:
        glossing = 'V'
        flex = flex % 1000 # auf 3 Stellen beschneiden, NomVf.-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex % 10 > 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid nominal verb form flexcode (pattern 7xx[1-5]x): '+str(flexcode))
        flex = flex // 10 # letzte Stelle abschneiden

        form = ''
        if   flex == 0:
            form = '\\nmlz/advz' # 60000, "subst/adv.verbf" (!unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Underspecified nominal/adverbial verb form flexcode (pattern 7x0xx): '+str(flexcode))
        elif flex == 1: form = '\\nmlz.m' # 60100, "verbalnomen.kzl"
        elif flex == 2: form = '\\nmlz.m' # 60200, "verbalnomen.endg w/j"
        elif flex == 3: form = '\\nmlz.f' # 60300, "verbalnomen.endg. t"
        elif flex == 4: form = '\\nmlz.f' # 60400, "verbalnomen.endg. wt/jt"
        elif flex == 5: form = '\\nmlz' # 60500, "verbalnomen gem"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid nominal verb form flexcode (pattern 7x[1-5]xx): '+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif (pos == 'adverb' and str(sub_pos) != 'prepositional_adverb') \
            or pos == 'substantive':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Komplementsinfinitive
    elif (flex // 1000) == 62:
        glossing = 'V\\adv.inf'
        flex = flex % 1000 # auf 3 Stellen beschneiden, KomplInf-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex % 10 > 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid complementary infinitive flexcode (pattern 62x0x): '+str(flexcode))
        flex = flex // 10 # letzte Stelle abschneiden

        form = ''
        if flex == 0: # 62000, "kompl.inf." (unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified(?) complementary infinitive flexcode (pattern 620?xx): '+str(flexcode))
        elif flex == 1: form = '.f' # 62100, "kompl.inf.endg.t"
        elif flex == 2: form = '.f' # 62200, "kompl.inf.endg.wt"
        elif flex == 3: form = '.f' # 62300, "kompl.inf.jt/yt"
        elif flex == 4: form = '.m' # 62400, "kompl.inf.gem."
        elif flex == 5: form = '.f' # 62500, "kompl.inf.gem.endg.t"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid complementary infinitive flexcode (pattern 62[1-5]0x): '+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'substantive':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Negativkomplement
    elif (flex // 1000) == 63:
        glossing = 'V\\advz'
        flex = flex % 1000 # auf 3 Stellen beschneiden, NegKompl-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex % 10 > 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid negative complement flexcode (pattern 63x0x): '+str(flexcode))
        flex = flex // 10 # letzte Stelle abschneiden

        form = ''
        if flex == 0: # 63000, "neg.kompl" (unterspezifiziert)
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified negative complement flexcode (pattern 630xx): '+str(flexcode))
        elif flex == 1: form = '' # 63100, "neg.kompl.kzl"
        elif flex == 2: form = '' # 63200, "neg.kompl.endg.w"
        elif flex == 3: form = '' # 63300, "neg.kompl.endg.t"
        elif flex == 4: form = '' # 63400, "neg.kompl.gem"
        elif flex == 5: form = '' # 63500, "neg.kompl.gem.endg.t"
        elif flex == 6: form = '' # 63600, "neg.kompl.gem.endg.w"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid negative complement flexcode (pattern 63[1-6]0x): '+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Infinitive
    elif (flex // 1000) == 61 or (((flex // 1000) >= 64) and ((flex // 1000) <= 69)):
        glossing = 'V\\inf'
        flex = flex % 1000 # auf 3 Stellen beschneiden, NegKompl-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        glossing += state

        #nicht existierende Codes nicht abgefangen

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'substantive':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Substantive
    elif (flex // 1000) == 70:
        glossing = 'N'
        flex = flex % 1000 # auf 3 Stellen beschneiden, KomplInf-Info weg

        #Status
        stateFlex = flex % 100 // 10 # vorletzte Stelle isolieren
        state = ''
        if stateFlex == 0: state = '' # sta oder unbekannt
        elif stateFlex == 5: state = ':stpr' # stpr
        elif stateFlex == 6: state = ':stc' # stc
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid substantive flexcode (state; pattern 70x[0/5/6]x): '+str(flexcode))

        #Suffixe
        stateFlex = flex % 10 # letzte Ziffer isolieren
        if stateFlex != 0: # stpr
            if state != ':stpr':
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Erroneous substantive stat.pr. flex code [state] (pattern 70x5x): '+str(flexcode))
                state = ':stpr'
        flex = flex // 100 # letzte beiden Stelle abschneiden, state-Info weg

        form = ''
        if flex == 0: form = ':sg' # sg
        elif flex == 1: form = ':pl' # pl
        elif flex == 3: form = ':du' # du
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid substantive flexcode (number; pattern 70[0/1/3]xx): '+str(flexcode))

        gender = ''
        if pos == 'substantive':
            if sub_pos == 'substantive_masc': gender ='.m'
            elif sub_pos == 'substantive_fem': gender ='.f'
            else:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified substantive form: no gender on noun ('+str(flexcode)+'): ' + glossing + gender + form + state)

        glossing += gender + form + state

        # Check POS compatibility
        if     pos == 'substantive' \
            or pos == 'entity_name' \
            or pos == 'epitheton_title' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'verb' \
            or pos == 'adjective' \
            or pos == 'pronoun' \
            or pos == 'numeral' \
            or pos == 'preposition' :
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Adjektive
    elif (flex // 1000) == 71:
        glossing = 'ADJ'
        if sub_pos == "nisbe_adjective_preposition":
            glossing = "PREP-adjz"
        elif sub_pos == "nisbe_adjective_substantive":
            glossing = "N-adjz"
        flex = flex % 1000 # auf 3 Stellen beschneiden, Adj-Info weg

        #Status
        stateFlex = flex // 100 # erste Ziffer isolieren

        form = ''
        state = ''
        if stateFlex == 0:
            state = '' # sta oder unbekannt
            flex = flex // 10 # erste beiden Ziffern isolieren ; ACHTUNG: Schenkels Neuerungen noch nicht berücksichtgt

            if flex == 0:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified adjective flexcode (number/gender; pattern 71000): '+str(flexcode))
            elif flex == 1: form = ':m.sg' #
            elif flex == 2: form = ':f.sg' #
            elif flex == 3: form = ':m.pl' #
            elif flex == 4: form = ':f.pl' #
            elif flex == 5: form = ':m.du' #
            elif flex == 6: form = ':f.du' #
            else:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adjective flexcode (number/gender; pattern 710[1-6]0): '+str(flexcode))

            if flexcode % 10 != 0:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adjective flexcode (Suffix without stat.pr.; pattern 711[0/1?-5/6?]0): '+str(flexcode))
        elif stateFlex == 1:
            state = '' # "stc", eigentlich Kompositum, z.B. ni-sw

            #enklitische Pronomina
            abhFlex = flex % 100 # letzte zwei Ziffern isolieren
            if abhFlex == 0: state = '' #
            elif ((abhFlex >= 1) and (abhFlex <= 9)):
                state = ':stpr' # stpr
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adjective flexcode (suffix pronoun instead of dep. pronoun; pattern 711[15-24]): '+str(flexcode))
            elif ((abhFlex >= 15) and (abhFlex <= 24)): state = '' # "stc"
            else:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adjective flexcode (pronoun; pattern 711[15-24]): '+str(flexcode))
        elif stateFlex == 2:
            state = ':stpr' # stpr redundant
            flex = flex // 10 # erste beiden Ziffern isolieren ; ACHTUNG: Schenkels Neuerungen noch nicht berücksichtgt

            if flex == 20: form = ':m.sg' # sic, verwirrend, dass bei 0 beginnend
            elif flex == 21: form = ':f.sg' #
            elif flex == 22: form = ':m.pl' #
            elif flex == 23: form = ':f.pl' #
            elif flex == 24: form = ':m.du' #
            elif flex == 25: form = ':f.du' #
            elif flex == 26: # 71260, "adj. in SK m. Präfix nꜣ (Einerstelle Suffixpr.) / Spätzeit [nꜣ:nfr=f]
                glossing = 'vblz-ADJ'
            else:
                if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adjective flexcode (number/gender; pattern 712[0-6]x): '+str(flexcode))

            #Suffixe
            state = stateFromSuffix (flexcode)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adjective flexcode (number/gender; pattern 71[0-2][0-6]x): '+str(flexcode))
        flex = flex % 10 # erste Stelle abschneiden, state-Info weg
        glossing += form + state

        # Check POS compatibility
        if     pos == 'adjective' \
            or pos == 'pronoun' \
            or pos == 'numeral' \
            or (pos == 'epitheton_title' and str(sub_pos) != 'title') \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'substantive' \
            or pos == 'entity_name' \
            or pos == 'epitheton_title' \
            or pos == 'preposition' \
            or pos == 'verb':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Adverbien
    elif (flex // 1000) == 72:
        glossing = 'ADV'
        flex = flex % 1000 # auf 3 Stellen beschneiden, NegKompl-Info weg

        #Suffixe
        state = ''
        stateFlex = flex % 10 # letzte Ziffer isolieren
        if stateFlex == 0: state = ':stpr' # st.pr. aber Suffix zerstört ## verwirrend
        else: state = ':stpr' # stpr
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex != 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid adverbial flexcode (pattern 7200x): '+str(flexcode))

        glossing += state

        # Check POS compatibility
        if     pos == 'adverb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'adjective' \
            or (pos == 'epitheton_title' and sub_pos != 'title') \
            or pos == 'preposition':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Zahlen
    elif (flex // 1000) == 74:
        glossing = 'NUM'
        flex = flex % 1000 # auf 3 Stellen beschneiden, NegKompl-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        form = ''
        subtype = ''
        if flex == 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified number form (pattern 7400x): '+str(flexcode))
        elif flex == 1:
            form = '.ord:sg.m' # immer sg?
            subtype = 'ordinal'
        elif flex == 2:
            form = '.ord:sg.f' # immer sg?
            subtype = 'ordinal'
        elif flex == 3:
            form = '.card:m' # wa, snwi
            subtype = 'cardinal'
        elif flex == 4:
            form = '.card:f' # wa.t, sn.ti
            subtype = 'cardinal'
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid number form (pattern 740[1-4]x): '+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        if     (pos == 'numeral' and str(sub_pos) == 'nan') \
            or str(sub_pos) == subtype \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'numeral' \
            or pos == 'substantive' \
            or pos == 'adjective' \
            or pos == 'epitheton_title':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Possessivartikel
    elif (flex // 100) == 800:
        glossing = 'ART.poss'
        flex = flex % 100 # auf 2 Stellen beschneiden, Possartikel-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex != 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid possessive article flexcode (pattern 8000x): '+str(flexcode))
        glossing += state

        # Check POS compatibility
        if     (pos == 'pronoun' and str(sub_pos) == 'nan') \
            or str(sub_pos) == 'demonstrative_pronoun' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'substantive' \
            or str(sub_pos) == 'personal_pronoun' \
            or (pos == 'adjective' and str(sub_pos) == 'nan'):
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Relativpronomina
    elif ((flex // 100) >= 801) and ((flex // 1000) <= 81):
        glossing = 'PRON.rel'
        flex = flex % 10000 # auf 4 Stellen beschneiden, RelPron-Info weg

        #Suffixe und enklitische Pronomina
        state = ''
        stateFlex = flex % 100 # letzte zwei Ziffern isolieren
        if stateFlex == 0: state = '' #
        elif ((stateFlex >= 1) and (stateFlex <= 9)): state = ':stpr' # stpr
        elif ((stateFlex >= 15) and (stateFlex <= 24)): state = '' # abh. Pronomen / "stc"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid relative pronoun flexcode (pronoun, pattern 8xx0x / 8xx15-24): '+str(flexcode))
        flex = flex // 100 # letzte zwei Stellen abschneiden, state-Info weg

        form = ''
        if   flex ==  0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified(?) relative pronoun form (pattern 8[0-1][1?-4]xx): '+str(flexcode))
        elif flex ==  1: form = ':m.sg' #
        elif flex ==  2: form = ':f.sg' #
        elif flex ==  3: form = ':m.pl' #
        elif flex ==  4: form = ':f.pl' #
        elif flex == 10:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Underspecified relative pronoun form (pattern 8[0-1][1?-4]xx): '+str(flexcode))
        elif flex == 11: form = ':m.sg' #
        elif flex == 12: form = ':f.sg' #
        elif flex == 13: form = ':m.pl' #
        elif flex == 14: form = ':f.pl' #
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid relative pronoun flexcode (gender/number, pattern 8[0-1][1-4]xx): '+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        if    (pos == 'pronoun' and str(sub_pos) == 'relative_pronoun') \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif  (pos == 'pronoun' and str(sub_pos) == 'nan') \
            or pos == 'substantive' \
            or pos == 'entity_name' \
            or (pos == 'adjective' and str(sub_pos) == 'nan') \
            or (pos == 'particle' and str(sub_pos) != 'particle_enclitic') \
            or str(sub_pos) == 'nisbe_adjective_preposition':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Admirativsuffix
    elif (flex // 1000) == 90:
        glossing = 'ADJ-excl'
        flex = flex % 1000 # auf 3 Stellen beschneiden, Possartikel-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex != 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid admirativ suffix flexcode (pattern 9000x): '+str(flexcode))
        glossing += state

        # Check POS compatibility
        if     pos == 'adjective' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'verb':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # sdm.tj.fj
    elif (flex // 100) == 910:
        glossing = 'V:ptcp.post'
        flex = flex % 100 # auf 2 Stellen beschneiden, Verbaladj-Info weg

        form = ''
        if   flex ==  0: form = '-m.sg' #
        elif flex == 10: form = '-f.sg' #
        elif flex == 20: form = '-m.pl' #
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid posterior participle flexcode (pattern 910[0-2]0): '+str(flexcode))
        glossing += form

        # Check POS compatibility
        if     pos == 'verb' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif (pos == 'adjective' and str(sub_pos) == 'nan'):
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Präpositionen
    elif (flex // 100) == 930:
        glossing = 'PREP'
        flex = flex % 100 # auf 2 Stellen beschneiden, Possartikel-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        if flex != 0:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid preposition flexcode (pattern 9300x): '+str(flexcode))
        glossing += state

        # Check POS compatibility
        if     pos == 'preposition' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif (pos == 'particle' and str(sub_pos) != 'particle_nonenclitic') \
            or str(sub_pos) == 'nisbe_adjective_preposition' \
            or str(sub_pos) == 'prepositional_adverb' \
            or pos == 'adverb' \
            or pos == 'adjective' \
            or pos == 'substantive' \
            or pos == 'entity_name' \
            or pos == 'epitheton_title' :
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Partikeln
    elif (flex // 100) == 940:
        glossing = 'PTCL'
        flex = flex % 100 # auf 2 Stellen beschneiden, Particle-Info weg

        #Suffixe und enklitische Pronomina
        state = ''
        stateFlex = flex % 100 # letzte zwei Ziffern isolieren
        if stateFlex == 0: state = '' #
        elif ((stateFlex >= 1) and (stateFlex <= 9)): state = ':stpr' # stpr
        elif ((stateFlex >= 15) and (stateFlex <= 24)): state = '' # "stc"
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid particle flexcode (pronoun; pattern 9400x, 94015-24): '+str(flexcode))

        glossing += state

        # Check POS compatibility
        if     pos == 'particle' \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'adverb' \
            or pos == 'interjection' \
            or pos == 'preposition' \
            or str(sub_pos) == 'interrogative_pronoun':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    # Auxilliar
    elif (flex // 1000) == 96:
        glossing = 'AUX'
        flex = flex % 1000 # auf 3 Stellen beschneiden, Aux-Info weg

        #Suffixe
        state = stateFromSuffix (flexcode)
        flex = flex // 10 # letzte Stelle abschneiden, state-Info weg

        form = ''
        if flex == 20: form = '' # (unspezifiziert)
        elif ((flex >= 30) and (flex <= 38)): form = '' #
        elif ((flex >= 40) and (flex <= 43)): form = '' #
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Invalid auxilliary flexcode (form, pattern 7620x, 7630x-43x):'+str(flexcode))
        glossing += form + state

        # Check POS compatibility
        #####warum tauch aux nicht in den pos/sub_pos auf??
        if     pos == 'verb' \
            or (pos == 'particle' and str(sub_pos) != 'particle_enclitic') \
            or pos == 'non valid lemma' \
            or pos == 'undefined':
                pass # ok
        elif pos == 'preposition':
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\t'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tWarning: Suspicious POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)
        else:
            if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Invalid POS<>flexcode combination: '+pos+'('+str(sub_pos)+')<>'+glossing)

    else:
        #unresolved
        glossing = lingGlossFromPOS(pos, sub_pos)
        if glossing == '':
            glossing = '(unresolved)'
        if logFile: logFile.write('\n'+pos+'\t'+str(sub_pos)+'\t'+str(flexcode)+'\tError: Unhandled flex code: '+str(flexcode))

    return glossing
