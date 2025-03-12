#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResistorCalcs.py - Utilities for resistor calculations in electronic design

This module provides functions for working with standard resistor series,
calculating parallel resistor combinations, and designing voltage dividers.
"""
from math import log10, floor, ceil
from typing import Dict, List, Tuple, Union, Optional, Any


def closest_e_value(value: float, series: int) -> float:
    """
    Find the closest standard resistor value from a given series.

    :param value: The target value to approximate.
    :param series: The standard series (3, 6, 12, 24, 48, 96, 192).
    :return: The closest standard value in the series.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    nh = next_higher_val(value, series)
    nl = next_lower_val(value, series)
    if (nh - value) > (value - nl):
        return nl
    else:
        return nh


def value_from_pos(ser_pos: int, series: int) -> float:
    """
    Converts a position in the standard resistor series to a value.

    Applies the conventional deviations from mathematical values that have been
    standardized in the industry. For example, a pure logarithmic division would
    give 4.6, but the standard E12 series uses 4.7 instead.

    :param ser_pos: The position in the series (zero-indexed).
    :param series: The standard series (e.g., 3, 6, 12, 24, 48, 96, 192).
    :return: The resistor value.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    (decade, dec_pos) = divmod(ser_pos, series)
    rounding = 2
    if series in {3, 6, 12, 24}:
        rounding = 1
    scale = round(10 ** (dec_pos / series), rounding)

    # Apply conventional adjustments to standard values
    if series == 3:
        if dec_pos == 2:
            scale += 0.1  # 4.6 is really 4.7
    elif series == 6:
        if dec_pos in {3, 4}:
            scale += 0.1  # Adjust values by 0.1
    elif series == 12:
        if dec_pos in {5, 6, 7, 8}:
            scale += 0.1  # Adjust values by 0.1
        elif dec_pos == 11:
            scale = 8.2  # 8.2 is the standard value
    elif series == 24:  # Many "standard" values in the E24 series require adjustment
        if dec_pos in {10, 11, 12, 13, 14, 15, 16}:
            scale += 0.1  # 2.6 - 4.6 are really 2.7 - 4.7
        elif dec_pos == 22:
            scale = 8.2  # 8.2 is the standard value
    elif series == 192:
        if scale == 9.19:
            scale = 9.20  # Historical convention

    value = round(scale * 10 ** decade, 10)
    if value > 0:
        return value
    return 0.0  # Fallback for invalid calculation


def e96_code_from_pos(pos: int) -> str:
    """
    Convert a position in the E96 series to a standard code.

    :param pos: The position in the E96 series.
    :return: The E96 code string (format: "##X" where ## is position and X is decade).
    """
    dec_dict = {0: "Y", 1: "X", 2: "A", 3: "H", 4: "C", 5: "D", 6: "E", 7: "F"}
    (decade, dec_pos) = divmod(pos, 96)
    return f"{(dec_pos + 1):02d}{dec_dict[decade]}"


def val_from_e96_code(code: str) -> Union[float, str]:
    """
    Convert an E96 code to its corresponding resistor value.

    :param code: The E96 code string.
    :return: The resistor value or an error message.
    """
    dec_dict = {
        "Y": 1, "R": 1, "X": 10, "A": 100, "H": 1000, "B": 1000,
        "C": 10000, "D": 100000, "E": 1000000, "F": 10000000
    }

    if len(code) != 3:
        return "Invalid code"

    try:
        print(f"Value code is {int(code[:2]):02d}, decade letter is {code[2]}")
        print(f"That gives a decade multiplier of {dec_dict[code[2]]}")
        print(f"The position value is {value_from_pos(int(code[:2]) - 1, 96)}")
        return value_from_pos(int(code[:2]) - 1, 96) * dec_dict[code[2]]
    except (ValueError, KeyError):
        print("Couldn't interpret that code")
        return "Invalid code"


def find_next_value(value: float, series: int, direction: str = "higher") -> float:
    """
    Finds the next standard value from a given series in the specified direction.

    :param value: The target value.
    :param series: The series to use (e.g., 3, 6, 12, 24, 48, 96, 192).
    :param direction: Either "higher" or "lower" to specify search direction.
    :return: The next value in the specified direction.
    :raises ValueError: If the series is invalid or the direction is not "higher" or "lower".
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    if direction not in ["higher", "lower"]:
        raise ValueError(f"Invalid direction: {direction}. Must be either 'higher' or 'lower'")

    # The logarithmic position calculation can sometimes miss the correct position
    # due to the variance between mathematical and standard values
    if direction == "lower":
        pos = floor(log10(value) * series) + 1
        step = -1
        comparison_func = lambda x, y: x <= y  # For "lower", we want values <= target
    else:  # direction == "higher"
        pos = ceil(log10(value) * series) - 1
        step = 1
        comparison_func = lambda x, y: x >= y  # For "higher", we want values >= target

    # Initial position check
    new_val = value_from_pos(pos, series)

    # Test multiple positions to ensure we get the correct 'next' value
    if comparison_func(new_val, value):
        return new_val
    elif comparison_func(value_from_pos(pos + step, series), value):
        return value_from_pos(pos + step, series)
    else:
        return value_from_pos(pos + 2 * step, series)


def next_lower_val(value: float, series: int) -> float:
    """
    Finds the next lower standard value from a given series.

    :param value: The target value.
    :param series: The series to use (e.g., 3, 6, 12, 24, 48, 96, 192).
    :return: The next lower value.
    :raises ValueError: If the series is invalid.
    """
    return find_next_value(value, series, "lower")


def next_higher_val(value: float, series: int) -> float:
    """
    Finds the next higher standard value from a given series.

    :param value: The target value.
    :param series: The series to use.
    :return: The next higher value.
    :raises ValueError: If the series is invalid.
    """
    return find_next_value(value, series, "higher")


def req_par_val(val_g: float, val1: float) -> float:
    """
    Calculates the required parallel resistance to achieve a goal resistance.

    :param val_g: The goal value.
    :param val1: The base resistance value.
    :return: The required parallel resistance value.
    """
    return (val_g * val1) / (val1 - val_g)


def par_pair_err(val: float, v1: float, v2: float) -> float:
    """
    Calculates the error percentage for a pair of resistors in parallel.

    :param val: The target value.
    :param v1: The first resistor value.
    :param v2: The second resistor value.
    :return: The percentage error.
    """
    return round(100 * ((v_par(v1, v2) - val) / val), 3)


def par_trip_err(val: float, v1: float, v2: float, v3: float) -> float:
    """
    Calculates the error percentage for three resistors in parallel.

    :param val: The target value.
    :param v1: The first resistor value.
    :param v2: The second resistor value.
    :param v3: The third resistor value.
    :return: The percentage error.
    """
    return round(100 * ((par_trips(v1, v2, v3) - val) / val), 5)


def v_par(v1: float, v2: float) -> float:
    """
    Calculates the value of two resistors in parallel.

    :param v1: The first resistor value.
    :param v2: The second resistor value.
    :return: The parallel resistance value.
    """
    return (v1 * v2) / (v1 + v2)


def next_h_pos(val: float, series: int) -> int:
    """
    Find the position of the next higher standard value.

    :param val: The target value.
    :param series: The series to use.
    :return: The position index.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    e = ceil(log10(val) * series) - 1
    if val <= value_from_pos(e, series):
        return e
    elif val <= value_from_pos(e + 1, series):
        return e + 1
    else:
        return e + 2


def next_l_pos(val: float, series: int) -> int:
    """
    Find the position of the next lower standard value.

    :param val: The target value.
    :param series: The series to use.
    :return: The position index.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    e = floor(log10(val) * series) + 1
    if val >= value_from_pos(e, series):
        return e
    elif val >= value_from_pos(e - 1, series):
        return e - 1
    else:
        return e - 2


def closest_pos(val: float, series: int) -> int:
    """
    Find the position of the closest standard value.

    :param val: The target value.
    :param series: The series to use.
    :return: The position index.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    up = next_h_pos(val, series)
    down = next_l_pos(val, series)
    if (value_from_pos(up, series) - val) > (val - value_from_pos(down, series)):
        return down
    else:
        return up


def get_err_field_abs(elem: Tuple) -> float:
    """
    Helper function to get the absolute error field from a tuple.
    Used as a key function for sorting.

    :param elem: A tuple containing the error value at index 3.
    :return: The absolute error value.
    """
    return abs(elem[3])


def get_err_trips_abs(elem: Tuple) -> float:
    """
    Helper function to get the absolute error field from a tuple for triplets.
    Used as a key function for sorting.

    :param elem: A tuple containing the error value at index 4.
    :return: The absolute error value.
    """
    return abs(elem[4])


def list_par_pairs(val: float, series: int) -> List[Tuple[float, float, float, float]]:
    """
    List all pairs of standard resistor values that can approximately achieve
    the desired value when connected in parallel.

    :param val: The target resistance value.
    :param series: The standard series to use.
    :return: A list of tuples (R1, R2, Rparallel, error%) sorted by error.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    e_min = next_h_pos(val, series)
    e_max = next_h_pos(2 * val, series)
    pairs = []

    for e in range(e_min, e_max):
        v1 = value_from_pos(e, series)  # First resistor
        v2e = req_par_val(val, v1)  # Second resistor exact value
        v2h = next_higher_val(v2e, series)  # Second resistor next higher value
        v2l = next_lower_val(v2e, series)  # Second resistor next lower value

        pairs.append((v1, v2h, v_par(v1, v2h), par_pair_err(val, v1, v2h)))
        pairs.append((v1, v2l, v_par(v1, v2l), par_pair_err(val, v1, v2l)))

    pairs.sort(key=get_err_field_abs)
    return pairs[0:220]


def par_trips(v1: float, v2: float, v3: float) -> float:
    """
    Calculate the equivalent resistance of three resistors in parallel.

    :param v1: The first resistor value.
    :param v2: The second resistor value.
    :param v3: The third resistor value.
    :return: The equivalent parallel resistance.
    """
    return v_par(v1, v_par(v3, v2))


def list_par_trips(val: float, series: int) -> List[Tuple[float, float, float, float, float]]:
    """
    List combinations of three standard resistor values that can approximately
    achieve the desired value when connected in parallel.

    :param val: The target resistance value.
    :param series: The standard series to use.
    :return: A list of tuples (R1, R2, R3, Rparallel, error%) sorted by error.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    e_min = next_h_pos(val, series)
    e_max = next_h_pos(3 * val, series)
    trips = []

    for e in range(e_min, e_max):
        v1 = closest_e_value(10 ** (e / series), series)
        v2e = req_par_val(val, v1)
        pairs = list_par_pairs(v2e, series)

        for item in pairs:
            trips.append((v1, item[0], item[1], par_trips(v1, item[0], item[1]),
                          par_trip_err(val, v1, item[0], item[1])))

    trips.sort(key=get_err_trips_abs)
    return trips[0:22]


def pretty_print(val: float) -> str:
    """
    Format a resistance value with appropriate suffix (k, M).

    :param val: The resistance value in ohms.
    :return: A formatted string.
    """
    if val < 1000:  # No suffix required
        return '{0:3g}'.format(val).lstrip()
    elif val < 1000000:
        return '{0:3g}k'.format(val / 1000).lstrip()
    else:
        return '{0:3g}M'.format(val / 1000000).lstrip()


def window_comp_res_string(v_nom: float, v_ref: float, v_tol: float, r_ser: float, series: int) -> None:
    """
    Calculate a 3-resistor string for generating the thresholds for a window comparator.

    :param v_nom: Nominal voltage.
    :param v_ref: Reference voltage.
    :param v_tol: Voltage tolerance.
    :param r_ser: Series resistance.
    :param series: The resistor series to use.
    :raises ValueError: If the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    # Determine basic division ratio of divider to match rail to reference
    div_rat = v_nom / v_ref
    # Calculate required fraction of total series resistance for each resistor
    f_bot = (1 - v_tol) * (1 / div_rat)
    f_mid = (2 * v_tol) * (1 / div_rat)
    f_top = 1 - (f_bot + f_mid)

    r_mid_actual = closest_e_value(f_mid * r_ser, series)
    r_bot_goal = r_mid_actual * f_bot / f_mid
    r_bot1 = next_lower_val(r_bot_goal, series)
    r_bot2 = closest_e_value(r_bot_goal - r_bot1, series)

    f_top_goal = r_mid_actual * f_top / f_mid
    r_top1 = next_lower_val(f_top * r_ser, series)
    r_top2 = closest_e_value(f_top_goal - r_top1, series)

    print("Real resistors")
    print(f"Top 1 : {pretty_print(r_top1)}Ω")
    print(f"Top 2 : {pretty_print(r_top2)}Ω")
    print(f"Middle : {pretty_print(r_mid_actual)}Ω")
    print(f"Bottom1: {pretty_print(r_bot1)}Ω")
    print(f"Bottom2: {pretty_print(r_bot2)}Ω")


def calc_operational_values(v_in: float, r_top: float, r_bot: float, d: float) -> Dict[str, Any]:
    """
    Given v_in, chosen r_top and r_bot, and desired division ratio d = v_out/v_in,
    compute operational characteristics.

    :param v_in: Input voltage.
    :param r_top: Top resistor value.
    :param r_bot: Bottom resistor value.
    :param d: Division ratio (v_out/v_in).
    :return: Dictionary with operational values.
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
        'constraint': None  # Will be set by the caller
    }


def calc_divider_candidates(v_in: float, v_out: float, series: int,
                            r_src_max: Optional[float] = None,
                            max_pd: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Calculate divider candidate(s) based on provided constraints.

    - If only r_src_max is provided, it selects the candidate that maximizes divider resistance
      (i.e. highest impedance, lowest power dissipation).

    - If only max_pd is provided, it selects the candidate that minimizes divider resistance
      (i.e. lowest impedance, highest power dissipation) based on the power in the larger resistor.

    - If both are provided, it calculates both candidates.

    :param v_in: Input voltage.
    :param v_out: Desired output voltage.
    :param series: The resistor series to use.
    :param r_src_max: Maximum source impedance constraint.
    :param max_pd: Maximum power dissipation constraint.
    :return: A list of candidate dictionaries.
    :raises ValueError: If no constraints are provided or if the series is invalid.
    """
    if series not in {3, 6, 12, 24, 48, 96, 192}:
        raise ValueError(f"Invalid series: {series}. Must be one of: 3, 6, 12, 24, 48, 96, 192")

    d = v_out / v_in
    candidates = []

    # Candidate based on maximum source impedance constraint:
    if r_src_max is not None:
        # R_src = R_bot * (1-d) <= r_src_max  -->  R_bot <= r_src_max / (1-d)
        r_bot_ideal = r_src_max / (1 - d)
        # Snap to a real resistor value (highest standard resistor not exceeding the ideal)
        r_bot_actual = next_lower_val(r_bot_ideal, series)
        # Calculate corresponding R_top using the divider ratio: R_top = R_bot*((1/d)-1)
        r_top_ideal = r_bot_actual * ((1 / d) - 1)
        r_top_actual = closest_e_value(r_top_ideal, series)
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
        r_bot_actual = next_higher_val(r_bot_ideal, series)
        r_top_ideal = r_bot_actual * ((1 / d) - 1)
        r_top_actual = closest_e_value(r_top_ideal, series)
        cand_pd = calc_operational_values(v_in, r_top_actual, r_bot_actual, d)
        cand_pd['constraint'] = 'max_pd'
        candidates.append(cand_pd)

    if not candidates:
        raise ValueError("At least one constraint must be specified (r_src_max and/or max_pd).")

    return candidates


def display_divider_candidates(v_in: float, v_out: float, series: int,
                               r_src_max: Optional[float] = None,
                               max_pd: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Calls calc_divider_candidates() and displays the results.

    :param v_in: Input voltage.
    :param v_out: Desired output voltage.
    :param series: The resistor series to use.
    :param r_src_max: Maximum source impedance constraint.
    :param max_pd: Maximum power dissipation constraint.
    :return: The candidate dictionaries.
    :raises ValueError: If no constraints are provided or if the series is invalid.
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
                pretty_print(cand['r_top']),
                pretty_print(cand['r_bot']),
                cand['r_src'],
                cand['v_out'],
                cand['p_top'] * 1000,
                cand['p_bot'] * 1000
            )
            print(row)

    return candidates


def print_divider_candidate(candidate: Dict[str, Any], v_in: float) -> None:
    """
    Print an ASCII diagram of a resistor divider based on the candidate data.

    :param candidate: A dictionary returned by calc_divider_candidates().
    :param v_in: Input voltage.
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
│ {pretty_print(r_top):^8}│  {1000 * p_top:.2f} mW
└────┬────┘
     │
     ├─── Vout = {v_out:.2f} V from {r_src:.2f} Ω
     │
┌────┴────┐      
│ {pretty_print(r_bot):^8}│  {1000 * p_bot:.2f} mW
└────┬────┘
     │
    GND
"""
    print(diagram)