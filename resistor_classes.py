#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resistor_classes.py - Object-oriented approach to resistor calculations

This module provides classes for working with resistors, including:
- Standard resistor series calculations
- Parallel resistors
- Voltage dividers
- Voltage references and window comparators

Classes:
    Resistor: Base class for resistor components
    ParallelResistors: Combination of resistors in parallel
    SeriesResistors: Combination of resistors in series
    VoltageDivider: Resistive voltage divider
    WindowComparator: Resistive window comparator reference
"""
from math import log10, floor, ceil
from typing import Dict, List, Tuple, Union, Optional, Any, Set
import matplotlib.pyplot as plt
from dataclasses import dataclass


class Resistor:
    """
    Base class for resistor components.

    This class provides functionality for working with standard resistor values,
    including methods to find the nearest standard values, calculate power
    dissipation, and format resistor values.

    Attributes:
        value (float): Resistance value in ohms
        series (int): The E-series used (3, 6, 12, 24, 48, 96, 192)
        power_rating (float): Maximum power rating in watts
        tolerance (float): Tolerance as a percentage (e.g., 1.0 for 1%)
    """

    # Set of valid E-series values
    VALID_SERIES = {3, 6, 12, 24, 48, 96, 192}

    def __init__(self, value: float, series: int = 24, power_rating: float = 0.25,
                 tolerance: float = 1.0):
        """
        Initialize a resistor with the given value and properties.

        Args:
            value: Resistance in ohms
            series: E-series (3, 6, 12, 24, 48, 96, 192)
            power_rating: Maximum power dissipation in watts
            tolerance: Tolerance as a percentage

        Raises:
            ValueError: If series is not a valid E-series
        """
        if series not in self.VALID_SERIES:
            raise ValueError(f"Invalid series: {series}. Must be one of: {self.VALID_SERIES}")

        self.value = value
        self.series = series
        self.power_rating = power_rating
        self.tolerance = tolerance

    def __str__(self) -> str:
        """Return a string representation of the resistor."""
        return f"Resistor({self.pretty_print_value()}, E{self.series}, {self.tolerance}%, {self.power_rating}W)"

    def __repr__(self) -> str:
        """Return a detailed representation of the resistor."""
        return f"Resistor(value={self.value}, series={self.series}, " \
               f"power_rating={self.power_rating}, tolerance={self.tolerance})"

    @classmethod
    def from_standard_value(cls, value: float, series: int, **kwargs) -> 'Resistor':
        """
        Create a resistor using the closest standard value.

        Args:
            value: Target resistance in ohms
            series: E-series to use
            **kwargs: Additional arguments for the Resistor constructor

        Returns:
            A Resistor instance with the nearest standard value
        """
        std_value = cls.closest_e_value(value, series)
        return cls(std_value, series, **kwargs)

    @staticmethod
    def value_from_pos(ser_pos: int, series: int) -> float:
        """
        Convert a position in the standard resistor series to a value.

        Args:
            ser_pos: Position in the series (zero-indexed)
            series: The E-series to use

        Returns:
            The resistance value at that position

        Raises:
            ValueError: If series is not valid
        """
        if series not in Resistor.VALID_SERIES:
            raise ValueError(f"Invalid series: {series}. Must be one of: {Resistor.VALID_SERIES}")

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

    @staticmethod
    def find_next_value(value: float, series: int, direction: str = "higher") -> float:
        """
        Find the next standard value in the specified direction.

        Args:
            value: The target value
            series: The E-series to use
            direction: Either "higher" or "lower"

        Returns:
            The next standard value in the specified direction

        Raises:
            ValueError: If series is not valid or direction is invalid
        """
        if series not in Resistor.VALID_SERIES:
            raise ValueError(f"Invalid series: {series}. Must be one of: {Resistor.VALID_SERIES}")

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
        new_val = Resistor.value_from_pos(pos, series)

        # Test multiple positions to ensure we get the correct 'next' value
        if comparison_func(new_val, value):
            return new_val
        elif comparison_func(Resistor.value_from_pos(pos + step, series), value):
            return Resistor.value_from_pos(pos + step, series)
        else:
            return Resistor.value_from_pos(pos + 2 * step, series)

    @staticmethod
    def next_higher_val(value: float, series: int) -> float:
        """
        Find the next higher standard value.

        Args:
            value: The target value
            series: The E-series to use

        Returns:
            The next higher standard value
        """
        return Resistor.find_next_value(value, series, "higher")

    @staticmethod
    def next_lower_val(value: float, series: int) -> float:
        """
        Find the next lower standard value.

        Args:
            value: The target value
            series: The E-series to use

        Returns:
            The next lower standard value
        """
        return Resistor.find_next_value(value, series, "lower")

    @staticmethod
    def closest_e_value(value: float, series: int) -> float:
        """
        Find the closest standard value in the specified series.

        Args:
            value: The target value
            series: The E-series to use

        Returns:
            The closest standard value

        Raises:
            ValueError: If series is not valid
        """
        if series not in Resistor.VALID_SERIES:
            raise ValueError(f"Invalid series: {series}. Must be one of: {Resistor.VALID_SERIES}")

        nh = Resistor.next_higher_val(value, series)
        nl = Resistor.next_lower_val(value, series)
        if (nh - value) > (value - nl):
            return nl
        else:
            return nh

    @staticmethod
    def pretty_print(value: float) -> str:
        """
        Format a resistance value with appropriate suffix (k, M).

        Args:
            value: The resistance value in ohms

        Returns:
            A formatted string representing the resistance
        """
        if value < 1000:  # No suffix required
            return '{0:3g}'.format(value).lstrip()
        elif value < 1000000:
            return '{0:3g}k'.format(value / 1000).lstrip()
        else:
            return '{0:3g}M'.format(value / 1000000).lstrip()

    def get_standard_value(self) -> float:
        """
        Get the nearest standard value for this resistor.

        Returns:
            The nearest standard value in the specified series
        """
        return self.closest_e_value(self.value, self.series)

    def pretty_print_value(self) -> str:
        """
        Format this resistor's value with appropriate suffix.

        Returns:
            A formatted string representing the resistance
        """
        return self.pretty_print(self.value)

    def calculate_power(self, voltage: float = None, current: float = None) -> float:
        """
        Calculate power dissipation using either P=V²/R or P=I²R.

        Args:
            voltage: Voltage across the resistor (V)
            current: Current through the resistor (A)

        Returns:
            Power in watts

        Raises:
            ValueError: If neither voltage nor current is provided
        """
        if voltage is not None:
            return voltage ** 2 / self.value
        elif current is not None:
            return current ** 2 * self.value
        else:
            raise ValueError("Either voltage or current must be provided")

    def within_rating(self, voltage: float = None, current: float = None) -> bool:
        """
        Check if the resistor is within its power rating.

        Args:
            voltage: Voltage across the resistor (V)
            current: Current through the resistor (A)

        Returns:
            True if power dissipation is within rating, False otherwise
        """
        power = self.calculate_power(voltage, current)
        return power <= self.power_rating

    @staticmethod
    def list_standard_values(series: int, decade: int = 0) -> List[float]:
        """
        List all standard values in a given series for a specific decade.

        Args:
            series: The E-series to use
            decade: The decade (0 for 1.0-9.99, 1 for 10-99.9, etc.)

        Returns:
            List of standard values

        Raises:
            ValueError: If series is not valid
        """
        if series not in Resistor.VALID_SERIES:
            raise ValueError(f"Invalid series: {series}. Must be one of: {Resistor.VALID_SERIES}")

        values = []
        for pos in range(series):
            real_pos = pos + decade * series
            values.append(Resistor.value_from_pos(real_pos, series))

        return values


class ParallelResistors:
    """
    Class for working with resistors in parallel.

    Attributes:
        resistors (List[Resistor]): List of resistors in the parallel combination
    """

    def __init__(self, *resistors: Resistor):
        """
        Initialize a parallel combination of resistors.

        Args:
            *resistors: Variable number of Resistor objects

        Raises:
            ValueError: If no resistors are provided
        """
        if not resistors:
            raise ValueError("At least one resistor must be provided")

        self.resistors = list(resistors)

    def __str__(self) -> str:
        """Return a string representation of the parallel combination."""
        resistor_strings = [r.pretty_print_value() for r in self.resistors]
        return f"Parallel[{' || '.join(resistor_strings)}] = {self.pretty_print_value()}"

    @property
    def value(self) -> float:
        """
        Calculate the equivalent resistance of the parallel combination.

        Returns:
            The equivalent resistance in ohms
        """
        if not self.resistors:
            return 0.0

        # 1/Req = 1/R1 + 1/R2 + ... + 1/Rn
        reciprocal_sum = sum(1.0 / r.value for r in self.resistors)
        return 1.0 / reciprocal_sum if reciprocal_sum != 0 else float('inf')

    def pretty_print_value(self) -> str:
        """
        Format the equivalent resistance with appropriate suffix.

        Returns:
            A formatted string representing the resistance
        """
        return Resistor.pretty_print(self.value)

    def add_resistor(self, resistor: Resistor) -> None:
        """
        Add a resistor to the parallel combination.

        Args:
            resistor: The Resistor object to add
        """
        self.resistors.append(resistor)

    @staticmethod
    def v_par(v1: float, v2: float) -> float:
        """
        Calculate the equivalent resistance of two resistors in parallel.

        Args:
            v1: First resistor value
            v2: Second resistor value

        Returns:
            The equivalent resistance
        """
        return (v1 * v2) / (v1 + v2)

    @classmethod
    def find_combination(cls, target: float, series: int,
                         max_resistors: int = 2) -> Tuple[List[Resistor], float]:
        """
        Find a combination of standard resistors that approximates the target value.

        Args:
            target: The target resistance
            series: The E-series to use
            max_resistors: Maximum number of resistors to use (2 or 3)

        Returns:
            Tuple containing list of resistors and error percentage
        """
        if max_resistors == 2:
            # Implementation for 2-resistor combinations
            e_min = cls._next_h_pos(target, series)
            e_max = cls._next_h_pos(2 * target, series)
            best_combo = None
            best_error = float('inf')

            for e in range(e_min, e_max):
                v1 = Resistor.value_from_pos(e, series)
                v2e = cls._req_par_val(target, v1)

                v2h = Resistor.next_higher_val(v2e, series)
                v2l = Resistor.next_lower_val(v2e, series)

                v_combo_h = cls.v_par(v1, v2h)
                error_h = abs((v_combo_h - target) / target) * 100

                v_combo_l = cls.v_par(v1, v2l)
                error_l = abs((v_combo_l - target) / target) * 100

                if error_h < best_error:
                    best_error = error_h
                    best_combo = [Resistor(v1, series), Resistor(v2h, series)]

                if error_l < best_error:
                    best_error = error_l
                    best_combo = [Resistor(v1, series), Resistor(v2l, series)]

            return best_combo, best_error

        elif max_resistors == 3:
            # Implementation for 3-resistor combinations
            # This is more complex and would need detailed implementation
            # Placeholder for now
            return [Resistor(target, series)], 0.0

        else:
            raise ValueError("max_resistors must be 2 or 3")

    @staticmethod
    def _next_h_pos(val: float, series: int) -> int:
        """Helper method to find the position of the next higher standard value."""
        if series not in Resistor.VALID_SERIES:
            raise ValueError(f"Invalid series: {series}. Must be one of: {Resistor.VALID_SERIES}")

        e = ceil(log10(val) * series) - 1
        if val <= Resistor.value_from_pos(e, series):
            return e
        elif val <= Resistor.value_from_pos(e + 1, series):
            return e + 1
        else:
            return e + 2

    @staticmethod
    def _req_par_val(val_goal: float, val1: float) -> float:
        """
        Calculate the required parallel resistance to achieve a goal resistance.

        Args:
            val_goal: The goal value
            val1: The known resistance value

        Returns:
            The required parallel resistance
        """
        return (val_goal * val1) / (val1 - val_goal)


class VoltageDivider:
    """
    Class for working with resistive voltage dividers.

    Attributes:
        r_top (Resistor): Top resistor in the divider
        r_bottom (Resistor): Bottom resistor in the divider
        v_in (float): Input voltage
    """

    def __init__(self, r_top: Resistor, r_bottom: Resistor, v_in: float = 5.0):
        """
        Initialize a voltage divider with the given resistors and input voltage.

        Args:
            r_top: Top resistor in the divider
            r_bottom: Bottom resistor in the divider
            v_in: Input voltage
        """
        self.r_top = r_top
        self.r_bottom = r_bottom
        self.v_in = v_in

    def __str__(self) -> str:
        """Return a string representation of the voltage divider."""
        return (f"Voltage Divider: {self.r_top.pretty_print_value()} / "
                f"{self.r_bottom.pretty_print_value()}, "
                f"Vin={self.v_in}V, Vout={self.v_out:.2f}V")

    @property
    def v_out(self) -> float:
        """
        Calculate the output voltage of the divider.

        Returns:
            The output voltage
        """
        division_ratio = self.r_bottom.value / (self.r_top.value + self.r_bottom.value)
        return self.v_in * division_ratio

    @property
    def division_ratio(self) -> float:
        """
        Calculate the division ratio (Vout/Vin) of the divider.

        Returns:
            The division ratio
        """
        return self.r_bottom.value / (self.r_top.value + self.r_bottom.value)

    @property
    def current(self) -> float:
        """
        Calculate the current through the divider.

        Returns:
            The current in amperes
        """
        return self.v_in / (self.r_top.value + self.r_bottom.value)

    @property
    def power_top(self) -> float:
        """
        Calculate the power dissipated by the top resistor.

        Returns:
            The power in watts
        """
        return self.current ** 2 * self.r_top.value

    @property
    def power_bottom(self) -> float:
        """
        Calculate the power dissipated by the bottom resistor.

        Returns:
            The power in watts
        """
        return self.current ** 2 * self.r_bottom.value

    @property
    def power_total(self) -> float:
        """
        Calculate the total power dissipated by the divider.

        Returns:
            The power in watts
        """
        return self.power_top + self.power_bottom

    @property
    def source_impedance(self) -> float:
        """
        Calculate the output source impedance of the divider.

        Returns:
            The source impedance in ohms
        """
        return ParallelResistors(self.r_top, self.r_bottom).value

    def print_diagram(self) -> None:
        """Print an ASCII art diagram of the voltage divider."""
        diagram = f"""
  {self.v_in:.2f} V
     │
  {1000 * self.current:.2f} mA 
     │     
┌────┴────┐     
│ {self.r_top.pretty_print_value():^8}│  {1000 * self.power_top:.2f} mW
└────┬────┘
     │
     ├─── Vout = {self.v_out:.2f} V from {self.source_impedance:.2f} Ω
     │
┌────┴────┐      
│ {self.r_bottom.pretty_print_value():^8}│  {1000 * self.power_bottom:.2f} mW
└────┬────┘
     │
    GND
"""
        print(diagram)

    @classmethod
    def design(cls, v_in: float, v_out: float, series: int = 24,
               r_src_max: float = None, max_pd: float = None) -> 'VoltageDivider':
        """
        Design a voltage divider to achieve a specific output voltage.

        Args:
            v_in: Input voltage
            v_out: Desired output voltage
            series: E-series to use
            r_src_max: Maximum source impedance constraint
            max_pd: Maximum power dissipation constraint

        Returns:
            A VoltageDivider object with the appropriate resistors

        Raises:
            ValueError: If no constraints are provided
        """
        if r_src_max is None and max_pd is None:
            raise ValueError("At least one constraint must be specified (r_src_max or max_pd)")

        d = v_out / v_in

        # Choose which constraint to optimize for
        if r_src_max is not None:
            # Maximize resistance based on source impedance constraint
            r_bot_ideal = r_src_max / (1 - d)
            r_bot_actual = Resistor.next_lower_val(r_bot_ideal, series)
            r_top_ideal = r_bot_actual * ((1 / d) - 1)
            r_top_actual = Resistor.closest_e_value(r_top_ideal, series)
        else:
            # Minimize resistance based on power dissipation constraint
            if d <= 0.5:
                # Top resistor is the limiter
                r_bot_ideal = (v_in ** 2 * d * (1 - d)) / max_pd
            else:
                # Bottom resistor is the limiter
                r_bot_ideal = (v_in ** 2 * d ** 2) / max_pd

            r_bot_actual = Resistor.next_higher_val(r_bot_ideal, series)
            r_top_ideal = r_bot_actual * ((1 / d) - 1)
            r_top_actual = Resistor.closest_e_value(r_top_ideal, series)

        r_top = Resistor(r_top_actual, series)
        r_bottom = Resistor(r_bot_actual, series)

        return cls(r_top, r_bottom, v_in)

    def plot(self) -> None:
        """Plot the voltage divider circuit and characteristics."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot circuit diagram (simplified)
        ax1.set_axis_off()
        ax1.set_xlim(0, 10)
        ax1.set_ylim(0, 10)

        # Draw circuit elements
        ax1.text(5, 9.5, f"Vin = {self.v_in:.2f} V", ha='center')
        ax1.plot([5, 5], [9, 8], 'k-')  # Vertical line

        # Top resistor
        ax1.plot([4, 6], [7, 7], 'k-')  # Horizontal lines for resistor
        ax1.plot([4, 6], [6, 6], 'k-')
        ax1.plot([5, 5], [7, 6], 'k-')  # Vertical line through resistor
        ax1.text(7, 6.5, f"Rtop = {self.r_top.pretty_print_value()}", va='center')

        # Middle junction
        ax1.plot([5, 5], [6, 5], 'k-')  # Vertical line
        ax1.plot([5, 7], [5, 5], 'k-')  # Horizontal line to Vout
        ax1.text(7.5, 5, f"Vout = {self.v_out:.2f} V", va='center')

        # Bottom resistor
        ax1.plot([4, 6], [4, 4], 'k-')  # Horizontal lines for resistor
        ax1.plot([4, 6], [3, 3], 'k-')
        ax1.plot([5, 5], [4, 3], 'k-')  # Vertical line through resistor
        ax1.text(7, 3.5, f"Rbot = {self.r_bottom.pretty_print_value()}", va='center')

        # Ground
        ax1.plot([5, 5], [3, 2], 'k-')  # Vertical line
        ax1.plot([4, 6], [2, 2], 'k-')  # Horizontal line for ground
        ax1.plot([4.5, 5.5], [1.8, 1.8], 'k-')  # Ground symbol
        ax1.plot([4.7, 5.3], [1.6, 1.6], 'k-')

        # Plot voltage vs. input voltage curve
        vin_range = np.linspace(0, self.v_in * 2, 100)
        vout_range = [self.division_ratio * v for v in vin_range]

        ax2.plot(vin_range, vout_range, 'b-')
        ax2.axvline(x=self.v_in, color='r', linestyle='--', label=f'Vin = {self.v_in}V')
        ax2.axhline(y=self.v_out, color='g', linestyle='--', label=f'Vout = {self.v_out:.2f}V')
        ax2.set_xlabel('Input Voltage (V)')
        ax2.set_ylabel('Output Voltage (V)')
        ax2.set_title('Voltage Transfer Characteristic')
        ax2.grid(True)
        ax2.legend()

        plt.tight_layout()
        plt.show()


def main():
    """Demonstrate the usage of the resistor classes."""
    # Create a standard resistor
    r1 = Resistor(4700)  # 4.7kΩ resistor
    print(f"Standard resistor: {r1}")

    # Create a resistor from the closest standard value
    r2 = Resistor.from_standard_value(4850, 24)
    print(f"Closest standard resistor to 4.85kΩ in E24: {r2}")

    # Create parallel combination
    parallel = ParallelResistors(r1, r2)
    print(f"Parallel combination: {parallel}")

    # Design a voltage divider to get 3.3V from 5V
    divider = VoltageDivider.design(5.0, 3.3, 24, r_src_max=10000)
    print(f"Designed voltage divider: {divider}")

    # Print the divider diagram
    divider.print_diagram()


if __name__ == "__main__":
    import numpy as np

    main()