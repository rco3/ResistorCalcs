#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 31 22:29:25 2020

@author: robolsen3
"""
from math import log10, floor, ceil


def Closest_E_Value(value: float, series: int):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        NH = Next_Higher_Val(value, series)
        NL = Next_Lower_Val(value, series)
        if (NH - value) > (value - NL):
           return NL
        else:
            return NH


def Value_From_Pos(serPos, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        (decade, decPos) = divmod(serPos, series)
        rounding = 2
        if series in {3, 6, 12, 24}:
            rounding = 1
        scale = round(10 ** (decPos / series), rounding)
        if series == 24:  # there are a lot of "standard" values in the E24 series.  We have to catch them and fix them.
            if decPos in {10, 11, 12, 13, 14, 15, 16}:
                scale += 0.1  # 2.6 - 4.6 are really 2.7 - 4.7
            elif decPos == 22:
                scale = 8.2  # 8.3 is mathematically correct, so we use 8.2
        elif series == 192:
            if scale == 9.19:
                scale = 9.20  # Ah, the rich tapestry of history
        value = round(scale * 10**decade, 10)
        if value > 0:
            return value


def Next_Lower_Val(value, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        Pos = floor(log10(value) * series)+1  # OH MY GOD I'm so lazy.  The variance between standard values and series
        newVal = Value_From_Pos(Pos, series)  # values means that there are situations in which the next lower value in
        if newVal < value:                      # the series is missed, in either direction (+1 position or -1)
            return newVal                       # so I just fucking TEST THEM ALL
        elif Value_From_Pos(Pos-1, series) < value:
            return Value_From_Pos(Pos-1, series)
        else:
            return Value_From_Pos(Pos-2, series)


def Next_Higher_Val(value, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        Pos = ceil(log10(value) * series)-1  # This mirrors my shame from Next_Lower_Val
        newVal = Value_From_Pos(Pos, series)
        if newVal > value:
            return newVal
        elif Value_From_Pos(Pos+1, series) > value:
            return Value_From_Pos(Pos+1, series)
        else:
            return Value_From_Pos(Pos+2, series)


def Req_Par_Val(ValG, Val1):
    """
    Given a goal value ValG and a base value Val1, find Val2 such that

    Val1 * Val2
    ----------- = ValG
    Val1 + Val2
    """
    return (ValG*Val1)/(Val1-ValG)


def ParPairErr(val, V1, V2):
    return round(100*((Vpar(V1, V2) - val)/val), 3)
    # See that '100*'?  That means this error is in %, baby!


def ParTripErr(val, V1, V2, V3):
    return round(100*((ParTrips(V1, V2, V3) - val)/val), 5)


def Vpar(V1, V2):
    return (V1 * V2) / (V1 + V2)


def Next_H_Pos(val, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        E = ceil(log10(val)*series)-1
        if val < Value_From_Pos(E, series):
            return E
        elif val < Value_From_Pos(E+1, series):
            return E+1
        else:
            return E+2


def Next_L_Pos(val, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        E = floor(log10(val)*series)+1
        if val > Value_From_Pos(E, series):
            return E
        elif val > Value_From_Pos(E-1, series):
            return E-1
        else:
            return E-2


def Closest_Pos(val, series):
    Up = Next_H_Pos(val, series)
    Down = Next_L_Pos(val, series)
    if (Value_From_Pos(Up, series)-val) > (val-Value_From_Pos(Down, series)):
        return Down
    else:
        return Up


def get_err_field_abs(elem):
    return abs(elem[3])


def get_err_trips_abs(elem):
    return abs(elem[4])


def List_Par_Pairs(val, series):
    """
    list all pairs of values in the series that
    can achieve the desired val
    """

    Emin = Next_H_Pos(val, series)
    Emax = Next_H_Pos(2 * val, series)
    pairs = list()
    for E in range(Emin, Emax):
        V1 = Value_From_Pos(E, series)
        # first resistor
        V2e = Req_Par_Val(val, V1)
        # second resistor exact value
        V2h = Next_Higher_Val(V2e, series)
        # second resistor next higher Series value
        V2l = Next_Lower_Val(V2e, series)
        # Second resistor next lower Series value
        pairs.append((V1, V2h, Vpar(V1, V2h), ParPairErr(val, V1, V2h)))
        pairs.append((V1, V2l, Vpar(V1, V2l), ParPairErr(val, V1, V2l)))

    pairs.sort(key=get_err_field_abs)
    # print("Best fit is", pairs[0][0], "in parallel with", pairs[0][1],
    #       "to get", pairs[0][2], "instead of", val, "for a",pairs[0][3],
    #       "% error." )

    return pairs[0:220]


def ParTrips(V1, V2, V3):
    return Vpar(V1, Vpar(V3, V2))


def List_Par_Trips(val, series):
    # cascade of List_Par_Pairs; after finding series V1, find ideal V2, then
    # find the closest series pairs to that value, and evaluate each such set
    # of three.
    Emin = Next_H_Pos(val, series)
    Emax = Next_H_Pos(3 * val, series)
    # print(Value_From_Pos(Emax, series))
    trips = list()
    for E in range(Emin, Emax):
        V1 = Closest_E_Value(10**(E/series), series)
        # first resistor
        V2e = Req_Par_Val(val, V1)
        pairs = List_Par_Pairs(V2e, series)
        for item in pairs:
            trips.append((V1, item[0], item[1], ParTrips(V1, item[0], item[1]),
                         ParTripErr(val, V1, item[0], item[1])))
    trips.sort(key=get_err_trips_abs)

    return trips[0:22]


def PrettyPrint(val):
    if val < 1000:  # no suffix required
        return '{0:3g}'.format(val).lstrip()
    elif val < 1000000:
        return '{0:3g}k'.format(val/1000).lstrip()
        # return '{:3g}k'.format(val/1000).lstrip()
    else:
        return '{0:3g}M'.format(val/1000000).lstrip()
        # return '{:3g}M'.format(val/1000000).lstrip()