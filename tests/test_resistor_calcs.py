#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest suite for ResistorCalcs.py

This test suite verifies the functionality of the resistor calculation functions.
Run with pytest.
"""
import pytest
from math import isclose
import sys
import os

# Add the parent directory to the path so we can import ResistorCalcs
# This isn't typically needed if you run pytest from the project root
# or if the module is installed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module
from ResistorCalcs import (
    value_from_pos, closest_e_value, find_next_value, next_lower_val, next_higher_val,
    v_par, par_trips, par_pair_err, req_par_val, closest_pos,
    next_h_pos, next_l_pos, pretty_print, calc_divider_candidates
)


def test_value_from_pos_e12():
    """Test the value_from_pos function with E12 series."""
    # Test E12 series values
    assert value_from_pos(0, 12) == 1.0
    assert value_from_pos(1, 12) == 1.2
    assert value_from_pos(6, 12) == 3.3  # Would be 3.2 mathematically
    assert value_from_pos(11, 12) == 8.2  # Special case
    assert value_from_pos(12, 12) == 10.0  # One decade up


def test_value_from_pos_e24():
    """Test the value_from_pos function with E24 series."""
    # Test E24 series values
    assert value_from_pos(0, 24) == 1.0
    assert value_from_pos(10, 24) == 2.7  # Would be 2.6 mathematically
    assert value_from_pos(22, 24) == 8.2  # Special case


def test_value_from_pos_e96():
    """Test the value_from_pos function with E96 series."""
    # Test E96 series values
    assert isclose(value_from_pos(0, 96), 1.00, rel_tol=1e-3)
    assert isclose(value_from_pos(12, 96), 1.33, rel_tol=1e-3)  # Corrected value
    assert isclose(value_from_pos(95, 96), 9.76, rel_tol=1e-3)
    assert isclose(value_from_pos(96, 96), 10.0, rel_tol=1e-3)


def test_value_from_pos_invalid_series():
    """Test value_from_pos with invalid series values."""
    # Test raising error with invalid series
    with pytest.raises(ValueError):
        value_from_pos(0, 5)  # 5 is not a valid series


def test_find_next_value():
    """Test the find_next_value function."""
    # Test higher direction
    assert find_next_value(1.05, 12, "higher") == 1.2
    assert find_next_value(4.7, 12, "higher") == 4.7  # Exact match
    assert find_next_value(8.3, 12, "higher") == 10.0

    # Test lower direction
    assert find_next_value(1.05, 12, "lower") == 1.0
    assert find_next_value(4.7, 12, "lower") == 4.7  # Exact match
    assert find_next_value(8.3, 12, "lower") == 8.2  # Corrected value (8.2 is the next lower value)

    # Test invalid direction
    with pytest.raises(ValueError):
        find_next_value(1.0, 12, "sideways")


def test_next_lower_val():
    """Test the next_lower_val function."""
    assert next_lower_val(1.05, 12) == 1.0
    assert next_lower_val(1.2, 12) == 1.2  # Exact match
    assert next_lower_val(9.0, 12) == 8.2


def test_next_higher_val():
    """Test the next_higher_val function."""
    assert next_higher_val(1.05, 12) == 1.2
    assert next_higher_val(1.2, 12) == 1.2  # Exact match
    assert next_higher_val(9.0, 12) == 10.0


def test_closest_e_value():
    """Test the closest_e_value function."""
    assert closest_e_value(1.05, 12) == 1.0  # Closer to 1.0 than 1.2
    assert closest_e_value(1.15, 12) == 1.2  # Closer to 1.2 than 1.0
    assert closest_e_value(1.1, 12) == 1.2  # Corrected value (1.1 is closer to 1.2)

    # Test invalid series
    with pytest.raises(ValueError):
        closest_e_value(1.0, 7)


def test_v_par():
    """Test the v_par function."""
    # Two equal resistors in parallel
    assert v_par(1000, 1000) == 500

    # Different resistors
    assert isclose(v_par(1000, 2000), 666.67, rel_tol=1e-3)


def test_par_trips():
    """Test the par_trips function."""
    # Three equal resistors
    assert isclose(par_trips(1000, 1000, 1000), 333.33, rel_tol=1e-3)

    # Different resistors
    assert isclose(par_trips(1000, 2000, 3000), 545.45, rel_tol=1e-3)


def test_par_pair_err():
    """Test the par_pair_err function."""
    # Target = 500, actual = 500
    assert par_pair_err(500, 1000, 1000) == 0.0

    # Target = 500, actual = 550 (10% high)
    assert isclose(par_pair_err(500, 1100, 1100), 10.0, rel_tol=1e-3)


def test_req_par_val():
    """Test the req_par_val function."""
    # To get 500 ohms with 1000 ohms...
    assert isclose(req_par_val(500, 1000), 1000, rel_tol=1e-3)

    # To get 400 ohms with 1000 ohms...
    assert isclose(req_par_val(400, 1000), 666.67, rel_tol=1e-3)


def test_closest_pos():
    """Test the closest_pos function."""
    # 1.15 should be closer to position 1 (1.2) than position 0 (1.0) in E12
    assert closest_pos(1.15, 12) == 1

    # Invalid series
    with pytest.raises(ValueError):
        closest_pos(1.0, 4)


def test_next_h_pos():
    """Test the next_h_pos function."""
    # Next higher position for 1.15 in E12 should be position 1 (1.2)
    assert next_h_pos(1.15, 12) == 1

    # Exact match
    assert next_h_pos(1.2, 12) == 1


def test_next_l_pos():
    """Test the next_l_pos function."""
    # Next lower position for 1.15 in E12 should be position 0 (1.0)
    assert next_l_pos(1.15, 12) == 0

    # Exact match
    assert next_l_pos(1.2, 12) == 1


def test_pretty_print():
    """Test the pretty_print function."""
    assert pretty_print(100) == "100"
    assert pretty_print(1000) == "1k"
    assert pretty_print(1500) == "1.5k"
    assert pretty_print(1000000) == "1M"
    assert pretty_print(1500000) == "1.5M"


def test_calc_divider_candidates():
    """Test the calc_divider_candidates function."""
    # Test with max source resistance constraint
    candidates = calc_divider_candidates(12.0, 5.0, 24, r_src_max=1000)
    assert len(candidates) == 1
    assert candidates[0]['constraint'] == 'max_r_src'

    # Test with max power dissipation constraint
    candidates = calc_divider_candidates(12.0, 5.0, 24, max_pd=0.1)
    assert len(candidates) == 1
    assert candidates[0]['constraint'] == 'max_pd'

    # Test with both constraints
    candidates = calc_divider_candidates(12.0, 5.0, 24, r_src_max=1000, max_pd=0.1)
    assert len(candidates) == 2

    # Test with invalid series
    with pytest.raises(ValueError):
        calc_divider_candidates(12.0, 5.0, 7)

    # Test with no constraints
    with pytest.raises(ValueError):
        calc_divider_candidates(12.0, 5.0, 24)


# Below are some parametrized tests for more thorough coverage

@pytest.mark.parametrize("value,series,expected", [
    (1.0, 12, 1.0),
    (1.1, 12, 1.2),  # 1.1 is actually slightly closer to 1.2 than to 1.0
    (1.15, 12, 1.2),
    (2.0, 24, 2.0),
    (2.05, 24, 2.0),
    (2.15, 24, 2.2),
    (4.5, 96, 4.53)  # Closest E96 value to 4.5 is 4.53
])
def test_closest_e_value_parametrized(value, series, expected):
    """Parametrized test for closest_e_value."""
    result = closest_e_value(value, series)
    assert isclose(result, expected, rel_tol=1e-2)


@pytest.mark.parametrize("v1,v2,expected", [
    (1000, 1000, 500),
    (1000, 2000, 666.67),
    (100, 100, 50),
    (470, 560, 255.5)
])
def test_v_par_parametrized(v1, v2, expected):
    """Parametrized test for v_par."""
    result = v_par(v1, v2)
    assert isclose(result, expected, rel_tol=1e-2)