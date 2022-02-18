#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 31 22:29:25 2020

@author: robolsen3
"""
from math import log10, floor, ceil


def Closest_E_Value(value, series):
    dec = floor(log10(value))
    # print(dec)
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        return round(10**(round(log10(value)*series)/series), 2 - dec)


def Value_From_Pos(Pos, series):
    return Closest_E_Value( 10**(Pos/series), series)


def Next_Lower_Val(value, series):
    dec = floor(log10(value))
    return round(10**(floor(log10(value)*series)/series), 2 - dec)


def Next_Higher_Val(value, series):
    dec = floor(log10(value))
    return round(10**(ceil(log10(value)*series)/series), 2 - dec)


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


def ParTripErr(val, V1, V2, V3):
    return round(100*((ParTrips(V1, V2, V3) - val)/val), 5)


def Vpar(V1, V2):
    return ((V1*V2)/(V1+V2))


def Next_H_Pos(val, series):
    E = ceil(log10(val)*series)
    if val < Value_From_Pos(E, series):
        return E
    else:
        return E+1


def Next_L_Pos(val, series):
    F = floor(log10(val)*series)
    if val > Value_From_Pos(F+1, series):
        return F+1
    return F


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