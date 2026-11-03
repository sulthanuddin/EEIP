
import math


def calculate_electrical_load(
    connected_load_kw: float,
    demand_factor: float,
    diversity_factor: float,
    power_factor: float,
    voltage: float,
    phase: str,
) -> dict:
    """
    Preliminary electrical load calculation.

    Diversity factor is defined as:
    Sum of individual maximum demands / coincident maximum demand.

    The scalar diversity factor approach must only be used when
    appropriate for the selected distribution system and design basis.
    """

    if connected_load_kw <= 0:
        raise ValueError("Connected load must be greater than zero.")

    if not 0 < demand_factor <= 1:
        raise ValueError("Demand factor must be greater than 0 and at most 1.")

    if diversity_factor < 1:
        raise ValueError("Diversity factor must be at least 1.")

    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be greater than 0 and at most 1.")

    if voltage <= 0:
        raise ValueError("Voltage must be greater than zero.")

    if phase not in ("Single Phase", "Three Phase"):
        raise ValueError("Select Single Phase or Three Phase.")

    # Preliminary demand calculation
    demand_load_kw = connected_load_kw * demand_factor

    # Apply diversity factor to the sum of individual maximum demands
    maximum_demand_kw = demand_load_kw / diversity_factor

    # Apparent power
    apparent_power_kva = maximum_demand_kw / power_factor

    # Full-load current
    if phase == "Three Phase":
        current_a = (
            apparent_power_kva * 1000
            / (math.sqrt(3) * voltage)
        )
    else:
        current_a = apparent_power_kva * 1000 / voltage

    return {
        "connected_load_kw": connected_load_kw,
        "demand_load_kw": demand_load_kw,
        "maximum_demand_kw": maximum_demand_kw,
        "apparent_power_kva": apparent_power_kva,
        "current_a": current_a,
        "power_factor": power_factor,
        "voltage": voltage,
        "phase": phase,
    }
