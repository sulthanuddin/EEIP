
import pytest

from app.modules.electrical_design.cable_sizing.voltage_drop import (
    calculate_design_current,
    calculate_voltage_drop,
    correct_resistance_for_temperature,
)


def test_three_phase_design_current():

    current = calculate_design_current(
        power_kw=30,
        voltage_v=400,
        power_factor=0.9,
        phase="Three Phase",
    )

    assert current == pytest.approx(48.1125, abs=0.001)


def test_single_phase_design_current():

    current = calculate_design_current(
        power_kw=5,
        voltage_v=230,
        power_factor=1.0,
        phase="Single Phase",
    )

    assert current == pytest.approx(21.73913)


def test_three_phase_voltage_drop():

    result = calculate_voltage_drop(
        current_a=50,
        length_m=100,
        voltage_v=400,
        power_factor=0.9,
        resistance_ohm_km=1.5,
        reactance_ohm_km=0.08,
        phase="Three Phase",
    )

    assert result["voltage_drop_v"] > 0
    assert result["voltage_drop_percent"] > 0


def test_single_phase_voltage_drop():

    result = calculate_voltage_drop(
        current_a=20,
        length_m=50,
        voltage_v=230,
        power_factor=1.0,
        resistance_ohm_km=2.0,
        reactance_ohm_km=0.1,
        phase="Single Phase",
    )

    assert result["voltage_drop_v"] == pytest.approx(4.0)


def test_copper_resistance_temperature_correction():

    resistance = correct_resistance_for_temperature(
        resistance_20c=1.0,
        operating_temperature_c=90,
        material="Copper",
    )

    assert resistance == pytest.approx(1.2751)


def test_invalid_power_factor():

    with pytest.raises(ValueError):

        calculate_design_current(
            power_kw=30,
            voltage_v=400,
            power_factor=0,
            phase="Three Phase",
        )


def test_invalid_phase():

    with pytest.raises(ValueError):

        calculate_design_current(
            power_kw=30,
            voltage_v=400,
            power_factor=0.9,
            phase="DC",
        )
