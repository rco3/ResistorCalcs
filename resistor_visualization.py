#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resistor_visualization.py - Demo for visualizing resistor circuits

This script demonstrates the visualization capabilities of the resistor_classes module,
particularly for voltage dividers, parallel resistors, and temperature effects.
"""

import numpy as np
import matplotlib

# Use Agg backend to avoid GUI dependencies and compatibility issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from resistor_classes import Resistor, ParallelResistors, VoltageDivider


def plot_e_series_distribution(series_list=[12, 24, 96], decade=0):
    """
    Plot the distribution of resistor values in different E-series.

    Args:
        series_list: List of E-series to plot (e.g., [12, 24, 96])
        decade: The decade to plot (0 for 1.0-9.99, 1 for 10-99.9, etc.)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['b', 'g', 'r', 'c', 'm']
    markers = ['o', 's', '^', 'x', 'd']

    for i, series in enumerate(series_list):
        values = Resistor.list_standard_values(series, decade)
        x = np.arange(len(values))

        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]

        ax.plot(x, values, f'{color}{marker}-', label=f'E{series}')
        ax.scatter(x, values, color=color, s=50)

        # Annotate values
        for j, val in enumerate(values):
            ax.annotate(f'{val:.2f}', (j, val), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=8, color=color)

    ax.set_xlabel('Position in Series')
    ax.set_ylabel('Resistance Value')
    ax.set_title(f'Distribution of E-series Resistor Values (Decade {decade})')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

    plt.tight_layout()
    plt.savefig('e_series_distribution.png')
    plt.close()
    print("Saved visualization to 'e_series_distribution.png'")


def plot_divider_load_effect(divider, load_resistances):
    """
    Plot the effect of loading a voltage divider with different load resistances.

    Args:
        divider: A VoltageDivider object
        load_resistances: List of load resistances to simulate
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    # Calculate the unloaded output voltage and source impedance
    v_unloaded = divider.v_out
    source_z = divider.source_impedance

    # Calculate loaded output voltages
    load_values = []
    v_loaded = []
    load_to_source_ratios = []

    for r_load in load_resistances:
        # Calculate the loaded output voltage using voltage divider principle
        # with the load resistor in parallel with the bottom resistor
        r_bottom_loaded = ParallelResistors(divider.r_bottom, Resistor(r_load)).value
        loaded_ratio = r_bottom_loaded / (divider.r_top.value + r_bottom_loaded)
        v_out_loaded = divider.v_in * loaded_ratio

        load_values.append(r_load)
        v_loaded.append(v_out_loaded)
        load_to_source_ratios.append(r_load / source_z)

    # Plot 1: Load resistance vs. output voltage
    ax1.semilogx(load_values, v_loaded, 'b-', linewidth=2)
    ax1.axhline(y=v_unloaded, color='r', linestyle='--',
                label=f'Unloaded: {v_unloaded:.2f}V')

    # Annotate key points
    ax1.axvline(x=source_z, color='g', linestyle='--',
                label=f'Source Z: {source_z:.1f}Ω')
    ax1.axvline(x=source_z * 10, color='g', linestyle=':', alpha=0.5,
                label=f'10x Source Z: {source_z * 10:.1f}Ω')

    ax1.set_xlabel('Load Resistance (Ω)')
    ax1.set_ylabel('Output Voltage (V)')
    ax1.set_title(
        f'Load Effect on Divider Output\nR_top={divider.r_top.pretty_print_value()}Ω, R_bot={divider.r_bottom.pretty_print_value()}Ω')
    ax1.grid(True)
    ax1.legend()

    # Plot 2: % voltage drop vs load resistance
    v_drop_pct = [(v_unloaded - v) / v_unloaded * 100 for v in v_loaded]
    ax2.semilogx(load_values, v_drop_pct, 'g-', linewidth=2)

    # Add region indicators
    ax2.axhspan(0, 1, alpha=0.2, color='green', label='<1% drop')
    ax2.axhspan(1, 5, alpha=0.2, color='yellow', label='1-5% drop')
    ax2.axhspan(5, 100, alpha=0.2, color='red', label='>5% drop')

    # Annotate source impedance lines
    ax2.axvline(x=source_z, color='g', linestyle='--',
                label=f'Source Z: {source_z:.1f}Ω')
    ax2.axvline(x=source_z * 10, color='g', linestyle=':', alpha=0.5,
                label=f'10x Source Z')

    ax2.set_xlabel('Load Resistance (Ω)')
    ax2.set_ylabel('Voltage Drop (%)')
    ax2.set_title('Percentage Voltage Drop Due to Loading')
    ax2.grid(True)
    ax2.legend()

    # Plot 3: Error vs Load/Source ratio
    ax3.semilogx(load_to_source_ratios, v_drop_pct, 'r-', linewidth=2)

    # Mark important ratios
    ax3.axvline(x=1, color='k', linestyle='--', label='1:1 Ratio')
    ax3.axvline(x=10, color='k', linestyle=':', label='10:1 Ratio')
    ax3.axvline(x=100, color='k', linestyle='-.', label='100:1 Ratio')

    # Add horizontal guidelines
    ax3.axhspan(0, 1, alpha=0.2, color='green')
    ax3.axhspan(1, 5, alpha=0.2, color='yellow')
    ax3.axhspan(5, 100, alpha=0.2, color='red')

    # Add annotations
    ax3.annotate('Rule of Thumb:\nLoad ≥ 10x Source Z\nfor < 10% error',
                 xy=(10, 9), xycoords='data',
                 xytext=(10, 20), textcoords='data',
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                 horizontalalignment='center', verticalalignment='bottom',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

    ax3.set_xlabel('Load/Source Impedance Ratio')
    ax3.set_ylabel('Voltage Error (%)')
    ax3.set_title('Error vs. Load/Source Impedance Ratio')
    ax3.grid(True)
    ax3.legend(loc='lower right')

    # Add overall figure title with source impedance info
    plt.suptitle(f'Voltage Divider Loading Analysis - Source Impedance: {source_z:.1f}Ω',
                 fontsize=16, y=0.98)

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    plt.savefig('divider_load_effect.png')
    plt.close()
    print("Saved visualization to 'divider_load_effect.png'")


def plot_divider_temp_effect(divider):
    """
    Plot the effect of temperature on a voltage divider's output with various TCR combinations.

    Args:
        divider: A VoltageDivider object
    """
    # Define temperature range and TCR combinations to test
    temp_range = (-40, 125)
    temps = np.linspace(temp_range[0], temp_range[1], 100)

    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(15, 12))

    # Define a set of TCR combinations to test
    tcr_combinations = [
        {'name': 'Matched (100/100)', 'top': 100, 'bottom': 100},
        {'name': 'Slightly Mismatched (100/50)', 'top': 100, 'bottom': 50},
        {'name': 'Mismatched (100/0)', 'top': 100, 'bottom': 0},
        {'name': 'Opposite (100/-100)', 'top': 100, 'bottom': -100},
        {'name': 'Highly Mismatched (200/50)', 'top': 200, 'bottom': 50}
    ]

    # Create subplots in a 3x2 grid
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # Plot 1: Comparison of voltage changes across TCR combinations
    ax1 = fig.add_subplot(gs[0, :])

    nominal_v_out = divider.v_out
    r_top_nominal = divider.r_top.value
    r_bottom_nominal = divider.r_bottom.value

    all_pct_changes = []

    for combo in tcr_combinations:
        tcr_top = combo['top']
        tcr_bottom = combo['bottom']

        v_out_values = []
        for temp in temps:
            delta_temp = temp - 25  # Difference from room temperature

            r_top = r_top_nominal * (1 + tcr_top * delta_temp / 1e6)
            r_bottom = r_bottom_nominal * (1 + tcr_bottom * delta_temp / 1e6)

            v_out = divider.v_in * (r_bottom / (r_top + r_bottom))
            v_out_values.append(v_out)

        # Calculate percentage change from nominal
        pct_change = [(v - nominal_v_out) / nominal_v_out * 100 for v in v_out_values]
        all_pct_changes.append(pct_change)

        # Plot the percentage change
        ax1.plot(temps, pct_change, linewidth=2, label=combo['name'])

    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Output Voltage Change (%)')
    ax1.set_title('Effect of TCR Matching on Voltage Stability')
    ax1.grid(True)
    ax1.legend(loc='best')

    # Find limits for consistent y-axis scaling
    max_dev = max([max(abs(min(pct)), abs(max(pct))) for pct in all_pct_changes])
    ax1.set_ylim(-max_dev * 1.1, max_dev * 1.1)

    # Plot individual TCR combinations in more detail
    for i, combo in enumerate(tcr_combinations[:4]):  # Show first 4 combinations in detail
        tcr_top = combo['top']
        tcr_bottom = combo['bottom']

        row = (i // 2) + 1
        col = i % 2

        ax = fig.add_subplot(gs[row, col])

        r_top_values = []
        r_bottom_values = []
        v_out_values = []

        for temp in temps:
            delta_temp = temp - 25

            r_top = r_top_nominal * (1 + tcr_top * delta_temp / 1e6)
            r_bottom = r_bottom_nominal * (1 + tcr_bottom * delta_temp / 1e6)

            v_out = divider.v_in * (r_bottom / (r_top + r_bottom))

            r_top_values.append(r_top)
            r_bottom_values.append(r_bottom)
            v_out_values.append(v_out)

        # Normalize resistance values for better visualization
        r_top_norm = [r / r_top_nominal for r in r_top_values]
        r_bottom_norm = [r / r_bottom_nominal for r in r_bottom_values]

        # Plot normalized resistance changes
        ax_twin = ax.twinx()
        ax.plot(temps, r_top_norm, 'r-', label=f'Top ({tcr_top} ppm/°C)')
        ax.plot(temps, r_bottom_norm, 'b-', label=f'Bottom ({tcr_bottom} ppm/°C)')

        # Plot voltage percentage change
        pct_change = [(v - nominal_v_out) / nominal_v_out * 100 for v in v_out_values]
        ax_twin.plot(temps, pct_change, 'g-', linewidth=2, label='Voltage Change')

        # Calculate min/max voltage change
        min_v_pct = min(pct_change)
        max_v_pct = max(pct_change)
        total_drift = max_v_pct - min_v_pct

        # Set labels and formatting
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Resistor Ratio to Nominal')
        ax_twin.set_ylabel('Voltage Change (%)')

        # Set title with drift information
        ax.set_title(f"{combo['name']}\nTotal Drift: {total_drift:.3f}%")

        # Add zero reference line for voltage change
        ax_twin.axhline(y=0, color='k', linestyle='-', alpha=0.3)

        # Set y limits for resistance ratio to make changes more visible
        y_min = min(min(r_top_norm), min(r_bottom_norm))
        y_max = max(max(r_top_norm), max(r_bottom_norm))
        padding = (y_max - y_min) * 0.1
        ax.set_ylim(y_min - padding, y_max + padding)

        # Set y limits for voltage change
        v_min = min(pct_change)
        v_max = max(pct_change)
        v_padding = (v_max - v_min) * 0.1
        ax_twin.set_ylim(v_min - v_padding, v_max + v_padding)

        # Add legends with appropriate positioning
        ax.legend(loc='upper left')
        ax_twin.legend(loc='upper right')

        # Add grid
        ax.grid(True, alpha=0.3)

    # Add TCR design guidelines in a text box
    guidelines = """TCR Design Guidelines:
1. Matched TCRs (same material): Minimal drift
2. Opposite TCRs can cancel but are rare
3. TCR mismatch effect increases with:
   - Greater temperature range
   - Larger TCR difference
   - Divider ratio closer to 50%"""

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.75, 0.25, guidelines, fontsize=12, verticalalignment='center',
             bbox=props, transform=fig.transFigure)

    plt.suptitle('Temperature Effects on Voltage Divider Performance', fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.savefig('divider_temp_effect.png')
    plt.close()
    print("Saved visualization to 'divider_temp_effect.png'")
    ax


def plot_parallel_combinations(target_value, series=24, max_error_pct=1.0):
    """
    Plot parallel resistor combinations that achieve a target value.

    Args:
        target_value: Target resistance
        series: E-series to use
        max_error_pct: Maximum allowed error percentage
    """
    # Get parallel resistor combinations - safely handle the case where req_par_val might fail
    try:
        # Try using the original method first
        from ResistorCalcs import list_par_pairs, pretty_print
        pairs = list_par_pairs(target_value, series)
        filtered_pairs = [p for p in pairs if abs(p[3]) <= max_error_pct]
    except Exception as e:
        print(f"Warning: Could not use list_par_pairs: {e}")
        print("Using alternative method to calculate parallel pairs...")

        # Alternative approach without using req_par_val directly
        filtered_pairs = []

        # Generate all resistor values to check in a few decades
        values = []
        for decade in range(-1, 3):  # Check a few decades
            for pos in range(series):
                values.append(Resistor.value_from_pos(pos + decade * series, series))

        # Try all combinations
        for i, r1 in enumerate(values):
            if r1 <= target_value:  # Skip values that would require negative second resistor
                continue

            for r2 in values[i:]:  # Only check combinations once (r1,r2 is same as r2,r1)
                # Calculate parallel equivalent
                if r1 + r2 == 0:  # Avoid division by zero
                    continue

                r_parallel = (r1 * r2) / (r1 + r2)
                error_pct = (r_parallel - target_value) / target_value * 100

                if abs(error_pct) <= max_error_pct:
                    filtered_pairs.append((r1, r2, r_parallel, error_pct))

        # Sort by absolute error
        filtered_pairs.sort(key=lambda x: abs(x[3]))

        # Use Resistor.pretty_print for formatting if imported method is unavailable
        if 'pretty_print' not in locals():
            pretty_print = Resistor.pretty_print

    if not filtered_pairs:
        print(f"No combinations with error <= {max_error_pct}% found.")
        return

    # Plot the combinations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Limit to top 100 combinations maximum for visualization
    display_pairs = filtered_pairs[:100]

    # Extract data for plotting
    r1_values = [p[0] for p in display_pairs]
    r2_values = [p[1] for p in display_pairs]
    r_parallel = [p[2] for p in display_pairs]
    errors = [p[3] for p in display_pairs]

    # Create a scatter plot of the combinations
    scatter = ax1.scatter(r1_values, r2_values, c=np.abs(errors),
                          cmap='viridis', alpha=0.7, s=100)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('Error (%)')

    # Plot diagonal line where R1 = R2
    max_val = max(max(r1_values), max(r2_values))
    min_val = min(min(r1_values), min(r2_values))
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)

    # Log scale for better visualization
    ax1.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_xlabel('R1 (Ω)')
    ax1.set_ylabel('R2 (Ω)')
    ax1.set_title(f'Parallel Combinations for {pretty_print(target_value)}Ω (E{series})')
    ax1.grid(True)

    # Add annotations for the best combinations
    best_idx = np.argmin(np.abs(errors))
    ax1.annotate(f"Best: {pretty_print(r1_values[best_idx])}Ω || {pretty_print(r2_values[best_idx])}Ω\n"
                 f"Error: {errors[best_idx]:.3f}%",
                 xy=(r1_values[best_idx], r2_values[best_idx]),
                 xytext=(r1_values[best_idx] * 1.5, r2_values[best_idx] * 1.5),
                 arrowprops=dict(arrowstyle='->'))

    # Plot error distribution
    ax2.bar(range(len(display_pairs)), np.abs(errors), alpha=0.7)
    ax2.axhline(y=np.abs(errors[best_idx]), color='r', linestyle='--',
                label=f'Best: {errors[best_idx]:.3f}%')

    ax2.set_xlabel('Combination Index')
    ax2.set_ylabel('Absolute Error (%)')
    ax2.set_title('Error Distribution of Parallel Combinations')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('parallel_combinations.png')
    plt.close()
    print("Saved visualization to 'parallel_combinations.png'")

    # Print the top 5 combinations
    print("Top 5 combinations:")
    for i, pair in enumerate(filtered_pairs[:5]):
        print(
            f"{i + 1}. {pretty_print(pair[0])}Ω || {pretty_print(pair[1])}Ω = {pretty_print(pair[2])}Ω (Error: {pair[3]:.3f}%)")


def visualize_divider_circuit(divider):
    """
    Visualize a voltage divider circuit with more detailed components.

    Args:
        divider: A VoltageDivider object
    """
    fig, ax = plt.subplots(figsize=(8, 10))

    # Set up the plot
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Circuit center x-coordinate for vertical alignment
    center_x = 5

    # Draw voltage source
    circle = plt.Circle((center_x, 10), 1, fill=False, linewidth=2)
    ax.add_patch(circle)
    ax.text(center_x, 10, f"{divider.v_in}V", ha='center', va='center')

    # Draw wire from source
    ax.plot([center_x, center_x], [9, 8], 'k-', linewidth=2)  # Vertical wire from source

    # Draw top resistor (zigzag)
    y_top = 8
    height_top = 3
    draw_resistor(ax, center_x, y_top, height_top, divider.r_top.value, divider.power_top)

    # Calculate midpoint between resistors
    y_mid = y_top - height_top - 0.5

    # Draw middle junction and Vout
    ax.plot([center_x, center_x], [y_top - height_top, y_mid], 'k-', linewidth=2)  # Vertical wire to midpoint
    ax.plot([center_x, center_x], [y_mid, y_mid - 0.5], 'k-', linewidth=2)  # Vertical wire to bottom resistor
    ax.plot([center_x, center_x + 3], [y_mid, y_mid], 'k-', linewidth=2)  # Horizontal wire to Vout

    # Vout marker
    ax.plot([center_x + 3, center_x + 3], [y_mid, y_mid - 0.5], 'k-', linewidth=2)  # Vout probe
    ax.text(center_x + 3, y_mid - 0.7, f"Vout = {divider.v_out:.3f}V", ha='center', va='top', color='blue')

    # Draw bottom resistor (zigzag)
    y_bot = y_mid - 1
    height_bot = 3
    draw_resistor(ax, center_x, y_bot, height_bot, divider.r_bottom.value, divider.power_bottom)

    # Draw ground
    ax.plot([center_x, center_x], [y_bot - height_bot, y_bot - height_bot - 0.3], 'k-', linewidth=2)  # Wire to ground
    draw_ground(ax, center_x, y_bot - height_bot - 0.3)

    # Add current labels
    ax.arrow(center_x + 0.3, y_top - 1, 0, -0.5, head_width=0.2, head_length=0.2,
             fc='red', ec='red', linewidth=1.5)
    ax.text(center_x + 0.6, y_top - 1.2, f"{divider.current * 1000:.2f} mA", color='red')

    # Add component values
    ax.text(center_x + 2, y_top - 1.5, f"R_top = {divider.r_top.pretty_print_value()}Ω\n"
                                       f"P_top = {divider.power_top * 1000:.2f} mW", va='center')

    ax.text(center_x + 2, y_bot - 1.5, f"R_bot = {divider.r_bottom.pretty_print_value()}Ω\n"
                                       f"P_bot = {divider.power_bottom * 1000:.2f} mW", va='center')

    # Add source impedance
    ax.text(center_x + 3, y_mid + 0.7, f"Source Impedance = {divider.source_impedance:.2f}Ω",
            ha='center', va='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Circuit title
    ax.set_title(f"Voltage Divider: {divider.division_ratio * 100:.1f}% of {divider.v_in}V")

    plt.tight_layout()
    plt.savefig('divider_circuit.png')
    plt.close()
    print("Saved visualization to 'divider_circuit.png'")


def draw_resistor(ax, x, y, height, value, power):
    """Helper function to draw a resistor symbol."""
    # Draw resistor zigzag
    segments = 6
    segment_height = height / segments
    width = 1.0

    for i in range(segments):
        if i % 2 == 0:
            ax.plot([x, x + width], [y - i * segment_height, y - (i + 1) * segment_height],
                    'k-', linewidth=2)
        else:
            ax.plot([x + width, x], [y - i * segment_height, y - (i + 1) * segment_height],
                    'k-', linewidth=2)

    # Check if power exceeds rating
    typical_rating = 0.25  # typical 1/4W resistor
    color = 'grey'
    if power > typical_rating:
        color = 'red'  # Highlight in red if power exceeds typical rating

    # Add background rectangle for the resistor
    rect = Rectangle((x - 0.3, y - height), width + 0.6, height,
                     facecolor=color, alpha=0.2, edgecolor='none')
    ax.add_patch(rect)


def draw_ground(ax, x, y):
    """Helper function to draw a ground symbol."""
    width = 0.8
    spacing = 0.15

    # Draw ground symbol
    for i in range(3):
        line_width = width - i * (width / 3)
        ax.plot([x - line_width / 2, x + line_width / 2],
                [y - i * spacing, y - i * spacing], 'k-', linewidth=2)


def main():
    """Demonstrate the visualization capabilities."""
    print("Resistor Visualization Demo")
    print("===========================")

    # Create a voltage divider (5V to 3.3V)
    divider = VoltageDivider.design(5.0, 3.3, 24, r_src_max=10000)
    print(f"Designed voltage divider: {divider}")

    # Display options
    print("\nVisualization Options:")
    print("1. Visualize voltage divider circuit")
    print("2. Show E-series distribution")
    print("3. Analyze divider load effect")
    print("4. Analyze temperature effects")
    print("5. Find parallel resistor combinations")
    print("6. Run all visualizations")

    try:
        choice = input("\nSelect visualization (1-6): ")
    except EOFError:
        # Default to run all visualizations in non-interactive environments
        choice = '6'
        print("Running all visualizations by default...")

    if choice == '1' or choice == '6':
        visualize_divider_circuit(divider)

    if choice == '2' or choice == '6':
        plot_e_series_distribution()

    if choice == '3' or choice == '6':
        # Create logarithmically spaced load resistances from 100Ω to 10MΩ
        loads = np.logspace(2, 7, 100)
        plot_divider_load_effect(divider, loads)

    if choice == '4' or choice == '6':
        # Analyze temperature effects with various TCR combinations
        plot_divider_temp_effect(divider)

    if choice == '5' or choice == '6':
        # Find parallel combinations for 3.3kΩ
        try:
            plot_parallel_combinations(3330, series=24, max_error_pct=0.5)
        except Exception as e:
            print(f"Error in parallel combinations plotting: {e}")
            # Fixed implementation without using req_par_val
            print("Using alternative implementation...")
            from ResistorCalcs import closest_e_value, v_par, par_pair_err

            target = 3300
            series = 24

            pairs = []
            for r1_pos in range(series * 3):  # Check a few decades
                r1 = Resistor.value_from_pos(r1_pos, series)
                if r1 <= target:
                    continue  # Skip resistors smaller than target (would need negative second resistor)

                # Try a range of r2 values
                for r2_pos in range(series * 3):
                    r2 = Resistor.value_from_pos(r2_pos, series)
                    parallel_val = v_par(r1, r2)
                    error = (parallel_val - target) / target * 100

                    if abs(error) <= 0.5:  # Max error threshold
                        pairs.append((r1, r2, parallel_val, error))

            # Sort by error magnitude
            pairs.sort(key=lambda x: abs(x[3]))

            # Print top 5 results
            print("Top 5 combinations (without using req_par_val):")
            for i, pair in enumerate(pairs[:5]):
                print(
                    f"{i + 1}. {Resistor.pretty_print(pair[0])}Ω || {Resistor.pretty_print(pair[1])}Ω = {Resistor.pretty_print(pair[2])}Ω (Error: {pair[3]:.3f}%)")

    print("\nVisualization complete!")


if __name__ == "__main__":
    main()