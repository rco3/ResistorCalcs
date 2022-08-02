# ResistorCalcs

Python module for mapping resistor values to standard E-series positions, and using positional information to calculate
optimal combinations (2 parallel -> goal value, 3 parallel -> goal value, etc). Includes "standard" values for all
E-series up to
E192 series.

The initial impetus for the module was the desire to take advantage of the incredible utility of using logs to find the
desired resistance value. Many operations are simplified in this way; however, the prevalence of "standard" values in
place of the mathematically-derived "correct" values (particularly in the E24 series) complicates this process, and
nullifies the ability to use the same, simple calculations everywhere. Instead, the mapping happens in one place and all
other functions call that for their operations.

Example usages include the creation of a list of resistance values for Unique Identifier tasks. Taking the case where a
5V supply is used, and it is desired to create 64 unique values, we can form a divider with the unknown resistances
against a local reference of 6.8k. Allowing for buffer zones at high and low voltages, let us set limits at 4.25V and
0.25V. I assume that the ADC reference and the divider supply are the same voltage.

```
Vs = np.arange(4.25, 0.25, -0.0625)

Rideals = [(5/V-1)*6800 for V in Vs]

Rpairs = [List_Par_Pairs(R,96)[:1] for R in Rideals]

 -- or --
 
Rpairs = [List_Par_Pairs(R,24)[0] for R in [(5/V-1)*6800 for V in np.arange(4.25, 0.25, -0.0625)]]
```

This will create a list of desired voltages, 16 per volt over a 4 volt range.

For each voltage desired, the resistance required to create that in a divider against 6.8k is computed. These will NOT
be standard values.

For each of these non-standard resistances, calculate the closest value achievable with two R24 resistors in parallel.
List_Par_Pairs sorts the response in ascending order of absolute error; the first in the list is the closest.
