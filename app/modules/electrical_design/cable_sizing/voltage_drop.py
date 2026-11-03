
import math


def calculate_design_current(
    power_kw,
    voltage_v,
    power_factor,
    phase,
    efficiency=1.0,
):
    """Calculate electrical input current."""

    values = [
        power_kw,
        voltage_v,
        power_factor,
        efficiency,
    ]

    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in values
    ):
        raise ValueError("Electrical inputs must be finite numbers.")

    if power_kw <= 0 or voltage_v <= 0:
        raise ValueError("Power and voltage must be positive.")

    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be between 0 and 1.")

    if not 0 < efficiency <= 1:
        raise ValueError("Efficiency must be between 0 and 1.")

    if phase == "Three Phase":

        return (
            power_kw * 1000
            / (
                math.sqrt(3)
                * voltage_v
                * power_factor
                * efficiency
            )
        )

    if phase == "Single Phase":

        return (
            power_kw * 1000
            / (
                voltage_v
                * power_factor
                * efficiency
            )
        )

    raise ValueError("Unsupported phase configuration.")


def calculate_voltage_drop(
    current_a,
    length_m,
    voltage_v,
    power_factor,
    resistance_ohm_km,
    reactance_ohm_km,
    phase,
):
    """
    Calculate approximate AC voltage drop.

    Length is one-way route length in metres.
    Resistance and reactance are ohms per kilometre.
    """

    numeric_values = [
        current_a,
        length_m,
        voltage_v,
        power_factor,
        resistance_ohm_km,
        reactance_ohm_km,
    ]

    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in numeric_values
    ):
        raise ValueError("Voltage-drop inputs must be finite numbers.")

    if (
        current_a <= 0
        or length_m <= 0
        or voltage_v <= 0
        or resistance_ohm_km <= 0
        or reactance_ohm_km < 0
    ):
        raise ValueError("Invalid voltage-drop input.")

    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be between 0 and 1.")

    if phase not in ("Single Phase", "Three Phase"):
        raise ValueError("Invalid phase configuration.")

    length_km = length_m / 1000

    sin_phi = math.sqrt(
        1 - power_factor ** 2
    )

    impedance_component = (
        resistance_ohm_km * power_factor
        + reactance_ohm_km * sin_phi
    )

    phase_factor = (
        2 if phase == "Single Phase"
        else math.sqrt(3)
    )

    voltage_drop_v = (
        phase_factor
        * current_a
        * length_km
        * impedance_component
    )

    voltage_drop_percent = (
        voltage_drop_v / voltage_v * 100
    )

    return {
        "voltage_drop_v": voltage_drop_v,
        "voltage_drop_percent": voltage_drop_percent,
        "receiving_voltage_v": voltage_v - voltage_drop_v,
        "length_km": length_km,
    }


def correct_resistance_for_temperature(
    resistance_20c,
    operating_temperature_c,
    material,
):
    """Correct conductor resistance using a linear temperature model."""

    if resistance_20c <= 0:
        raise ValueError("Resistance must be positive.")

    if material == "Copper":
        alpha = 0.00393

    elif material == "Aluminium":
        alpha = 0.00403

    else:
        raise ValueError("Unsupported conductor material.")

    return (
        resistance_20c
        * (
            1
            + alpha * (operating_temperature_c - 20)
        )
    )
