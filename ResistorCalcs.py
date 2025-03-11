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
    """
    Converts a position in the standard resistor series to a value.

    :param serPos: The position in the series (zero-indexed).
    :param series: The standard series (e.g., 3, 6, 12, 24, 48, 96, 192).
    :return: The resistor value.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        (decade, decPos) = divmod(serPos, series)
        rounding = 2
        if series in {3, 6, 12, 24}:
            rounding = 1
        scale = round(10 ** (decPos / series), rounding)
        if series == 3:
            if decPos == 2:
                scale += 0.1  # 4.6 is really 4.7
        if series == 6:
            if decPos in {3, 4}:
                scale += 0.1
        if series == 12:
            if decPos in {5, 6, 7, 8}:
                scale += 0.1
            elif decPos == 11:
                scale = 8.2
        if series == 24:  # there are a lot of "standard" values in the E24 series.  We have to catch them and fix them.
            if decPos in {10, 11, 12, 13, 14, 15, 16}:
                scale += 0.1  # 2.6 - 4.6 are really 2.7 - 4.7
            elif decPos == 22:
                scale = 8.2  # 8.3 is mathematically correct, so we use 8.2
        elif series == 192:
            if scale == 9.19:
                scale = 9.20  # Ah, the rich tapestry of history
        value = round(scale * 10 ** decade, 10)
        if value > 0:
            return value


def E96_Code_from_pos(pos: int):
    decDict = {0: "Y", 1: "X", 2: "A", 3: "H", 4: "C", 5: "D", 6: "E", 7: "F", }
    (decade, decPos) = divmod(pos, 96)
    return f"{(decPos + 1):02d}{decDict[decade]}"


def Val_from_E96_code(code: str):
    decDict = {"Y": 1, "R": 1, "X": 10, "A": 100, "H": 1000, "B": 1000, "C": 10000, "D": 100000, "E": 1000000,
               "F": 10000000, }
    if len(code) != 3:
        return "Invalid code"
    else:
        try:
            print(f"Value code is {int(code[:2]):02d}, decade letter is {code[2]}")
            print(f"That gives a decade multiplier of {decDict[code[2]]}")
            print(f"The position value is {Value_From_Pos(int(code[:2]) - 1, 96)}")
            return Value_From_Pos(int(code[:2]) - 1, 96) * decDict[code[2]]
        except ValueError:
            print("Couldn't interpret that code")


def Next_Lower_Val(value, series):
    """
    Finds the next lower standard value from a given series, that is not greater than the specified value.

    :param value: The target value.
    :param series: The series to use (e.g., 3, 6, 12, 24, 48, 96, 192).
    :return: The next lower value or 0 if the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        Pos = floor(
            log10(value) * series) + 1  # OH MY GOD I'm so lazy.  The variance between standard values and series
        newVal = Value_From_Pos(Pos, series)  # values means that there are situations in which the next lower value in
        if newVal <= value:  # the series is missed, in either direction (+1 position or -1)
            return newVal  # so I just fucking TEST THEM ALL
        elif Value_From_Pos(Pos - 1, series) < value:
            return Value_From_Pos(Pos - 1, series)
        else:
            return Value_From_Pos(Pos - 2, series)


def Next_Higher_Val(value, series):
    """
    Finds the next higher standard value from a given series, that is not less than the specified value.

    :param value: The target value.
    :param series: The series to use.
    :return: The next higher value or 0 if the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        Pos = ceil(log10(value) * series) - 1  # This mirrors my shame from Next_Lower_Val
        newVal = Value_From_Pos(Pos, series)
        if newVal >= value:
            return newVal
        elif Value_From_Pos(Pos + 1, series) > value:
            return Value_From_Pos(Pos + 1, series)
        else:
            return Value_From_Pos(Pos + 2, series)


def Req_Par_Val(ValG, Val1):
    """
    Calculates the required parallel resistance value to achieve a specified goal resistance.

    :param ValG: The goal value.
    :param Val1: The base resistance value.
    :return: The required parallel resistance value.
    """
    return (ValG * Val1) / (Val1 - ValG)


def ParPairErr(val, V1, V2):
    """
    Calculates the error percentage for a pair of resistors in parallel.

    :param val: The target value.
    :param V1: The first resistor value.
    :param V2: The second resistor value.
    :return: The percentage error.
    """
    return round(100 * ((Vpar(V1, V2) - val) / val), 3)
    # See that '100*'?  That means this error is in %, baby!


def ParTripErr(val, V1, V2, V3):
    return round(100 * ((ParTrips(V1, V2, V3) - val) / val), 5)


def Vpar(V1, V2):
    """
    Calculates the value of two resistors in parallel.

    :param V1: The first resistor value.
    :param V2: The second resistor value.
    :return: The parallel resistance value.
    """
    return (V1 * V2) / (V1 + V2)


def Next_H_Pos(val, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        E = ceil(log10(val) * series) - 1
        if val <= Value_From_Pos(E, series):
            return E
        elif val <= Value_From_Pos(E + 1, series):
            return E + 1
        else:
            return E + 2


def Next_L_Pos(val, series):
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        return 0
    else:
        E = floor(log10(val) * series) + 1
        if val >= Value_From_Pos(E, series):
            return E
        elif val >= Value_From_Pos(E - 1, series):
            return E - 1
        else:
            return E - 2


def Closest_Pos(val, series):
    Up = Next_H_Pos(val, series)
    Down = Next_L_Pos(val, series)
    if (Value_From_Pos(Up, series) - val) > (val - Value_From_Pos(Down, series)):
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
        V1 = Closest_E_Value(10 ** (E / series), series)
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
        return '{0:3g}k'.format(val / 1000).lstrip()
        # return '{:3g}k'.format(val/1000).lstrip()
    else:
        return '{0:3g}M'.format(val / 1000000).lstrip()
        # return '{:3g}M'.format(val/1000000).lstrip()


"""
Calculate a 3-resistor string for generating the thresholds for a window comparator
"""


def WindowCompResString(Vnom, Vref, VTol, Rser, series):
    # determine basic division ratio of divider to match rail to reference
    DivRat = Vnom / Vref
    # calculate required fraction of total series resistance needed for each resistor in the stack.
    Fbot = (1 - VTol) * (1 / DivRat)
    Fmid = (2 * VTol) * (1 / DivRat)
    Ftop = 1 - (Fbot + Fmid)
    RmidActual = Closest_E_Value(Fmid * Rser, series)
    RbotGoal = RmidActual * Fbot / Fmid
    Rbot1 = Next_Lower_Val(RbotGoal, series)
    Rbot2 = Closest_E_Value(RbotGoal - Rbot1, series)
    FtopGoal = RmidActual * Ftop / Fmid
    Rtop1 = Next_Lower_Val(Ftop * Rser, series)
    Rtop2 = Closest_E_Value(FtopGoal - Rtop1, series)
    print("Real resistors")
    print(f"Top 1 : {PrettyPrint(Rtop1)}Ω")
    print(f"Top 2 : {PrettyPrint(Rtop2)}Ω")
    print(f"Middle : {PrettyPrint(RmidActual)}Ω")
    print(f"Bottom1: {PrettyPrint(Rbot1)}Ω")
    print(f"Bottom2: {PrettyPrint(Rbot2)}Ω")
    # print(f"Errors: Bottom {100*(1-(((Rbot1+Rbot2)/RmidActual)/(Fbot/Fmid))):.3f}%, Top {100*(1-(RmidActual/(Rtop1+Rtop2))/(Fmid/Ftop)):.3f}%")


def calc_operational_values(v_in, r_top, r_bot, d):
    """
    Given v_in, chosen r_top and r_bot, and desired division ratio d = v_out/v_in,
    compute operational characteristics.
    """
    r_src = (r_top * r_bot) / (r_top + r_bot)
    v_out_actual = v_in * (r_bot / (r_top + r_bot))
    p_bot = (v_out_actual ** 2) / r_bot
    p_tot = (v_in ** 2) / (r_top + r_bot)
    p_top = p_tot - p_bot
    i_div = v_in / (r_top + r_bot)
    return {
        'r_top': r_top,
        'r_bot': r_bot,
        'r_src': r_src,
        'v_out': v_out_actual,
        'p_top': p_top,
        'p_bot': p_bot,
        'i_div': i_div,
        'constraint': None  # will be set by the caller
    }


def calc_divider_candidates(v_in, v_out, series, r_src_max=None, max_pd=None):
    """
    Calculate divider candidate(s) based on provided constraints.

    - If only r_src_max is provided, it selects the candidate that maximizes divider resistance
      (i.e. highest impedance, lowest power dissipation).

    - If only max_pd is provided, it selects the candidate that minimizes divider resistance
      (i.e. lowest impedance, highest power dissipation) based on the power in the larger resistor.

      For the max_pd candidate:
        - If d <= 0.5 (lower V_out relative to V_in), then R_top is the limiter:
              R_bot >= (v_in^2 * d * (1-d)) / max_pd
        - If d >= 0.5, then R_bot is the limiter:
              R_bot >= (v_in^2 * d^2) / max_pd

    - If both are provided, it calculates both candidates.

    Returns:
      A list of candidate dictionaries.
    """
    d = v_out / v_in
    candidates = []

    # Candidate based on maximum source impedance constraint:
    if r_src_max is not None:
        # R_src = R_bot * (1-d) <= r_src_max  -->  R_bot <= r_src_max / (1-d)
        r_bot_ideal = r_src_max / (1 - d)
        # Snap to a real resistor value (highest standard resistor not exceeding the ideal)
        r_bot_actual = Next_Lower_Val(r_bot_ideal, series)
        # Calculate corresponding R_top using the divider ratio: R_top = R_bot*((1/d)-1)
        r_top_ideal = r_bot_actual * ((1 / d) - 1)
        r_top_actual = Closest_E_Value(r_top_ideal, series)
        cand_imp = calc_operational_values(v_in, r_top_actual, r_bot_actual, d)
        cand_imp['constraint'] = 'max_r_src'
        candidates.append(cand_imp)

    # Candidate based on maximum power dissipation constraint:
    if max_pd is not None:
        if d <= 0.5:
            # Top resistor is the limiter:
            # P_top = (v_in^2 * d * (1-d)) / R_bot <= max_pd  -->  R_bot >= (v_in^2 * d * (1-d)) / max_pd
            r_bot_ideal = (v_in ** 2 * d * (1 - d)) / max_pd
        else:
            # Bottom resistor is the limiter:
            # P_bot = (v_in^2 * d^2) / R_bot <= max_pd  -->  R_bot >= (v_in^2 * d^2) / max_pd
            r_bot_ideal = (v_in ** 2 * d ** 2) / max_pd

        # Snap to the next higher standard resistor value (to ensure power remains below the limit)
        r_bot_actual = Next_Higher_Val(r_bot_ideal, series)
        r_top_ideal = r_bot_actual * ((1 / d) - 1)
        r_top_actual = Closest_E_Value(r_top_ideal, series)
        cand_pd = calc_operational_values(v_in, r_top_actual, r_bot_actual, d)
        cand_pd['constraint'] = 'max_pd'
        candidates.append(cand_pd)

    if not candidates:
        raise ValueError("At least one constraint must be specified (r_src_max and/or max_pd).")

    return candidates


def display_divider_candidates(v_in, v_out, series, r_src_max=None, max_pd=None):
    """
    Calls calc_divider_candidates() and displays the results:

      - If only one candidate is computed (i.e. one constraint provided),
        print an ASCII art diagram (via print_divider_candidate).

      - If both constraints are provided (two candidates),
        print a simple table with headers.

    Returns:
      The candidate dictionary (or list of dictionaries) from calc_divider_candidates().
    """
    candidates = calc_divider_candidates(v_in, v_out, series, r_src_max, max_pd)

    if len(candidates) == 1:
        # Use the detailed ASCII art output.
        print_divider_candidate(candidates[0], v_in)
    elif len(candidates) == 2:
        # Print a simple table with headers.
        header = "{:<12} {:<12} {:<12} {:<12} {:<12} {:<14} {:<14}".format(
            "Constraint", "R_top", "R_bot", "R_src", "V_out", "P_top (mW)", "P_bot (mW)"
        )
        print(header)
        print("-" * len(header))
        for cand in candidates:
            row = "{:<12} {:<12} {:<12} {:<12.2f} {:<12.2f} {:<14.2f} {:<14.2f}".format(
                cand['constraint'],
                PrettyPrint(cand['r_top']),
                PrettyPrint(cand['r_bot']),
                cand['r_src'],
                cand['v_out'],
                cand['p_top'] * 1000,
                cand['p_bot'] * 1000
            )
            print(row)

    return candidates


def print_divider_candidate(candidate, v_in):
    """
    Print an ASCII diagram of a resistor divider based on the candidate data.

    The candidate is a dictionary returned by calc_divider_candidates().
    """
    r_top = candidate['r_top']
    r_bot = candidate['r_bot']
    r_src = candidate['r_src']
    v_out = candidate['v_out']
    p_top = candidate['p_top']
    p_bot = candidate['p_bot']
    i_div = candidate['i_div']

    diagram = f"""
  {v_in:.2f} V
     │
  {1000 * i_div:.2f} mA 
     │     
┌────┴────┐     
│ {PrettyPrint(r_top):^8}│  {1000 * p_top:.2f} mW
└────┬────┘
     │
     ├─── Vout = {v_out:.2f} V from {r_src:.2f} Ω
     │
┌────┴────┐      
│ {PrettyPrint(r_bot):^8}│  {1000 * p_bot:.2f} mW
└────┬────┘
     │
    GND
"""
    print(diagram)
