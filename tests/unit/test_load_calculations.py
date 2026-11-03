
import pytest

from app.modules.electrical_design.load_calculations import (
    calculate_electrical_load,
)


def test_three_phase_load_calculation():

    result = calculate_electrical_load(
        connected_load_kw=100,
        demand_factor=0.8,
        diversity_factor=1.2,
        power_factor=0.9,
        voltage=400,
        phase="Three Phase",
    )

    assert result["connected_load_kw"] == pytest.approx(100)
    assert result["demand_load_kw"] == pytest.approx(80)
    assert result["maximum_demand_kw"] == pytest.approx(66.6666667)
    assert result["apparent_power_kva"] == pytest.approx(74.074074)
    assert result["current_a"] == pytest.approx(106.90, abs=0.02)


def test_single_phase_load_calculation():

    result = calculate_electrical_load(
        connected_load_kw=10,
        demand_factor=1.0,
        diversity_factor=1.0,
        power_factor=1.0,
        voltage=230,
        phase="Single Phase",
    )

    assert result["current_a"] == pytest.approx(43.47826)


def test_invalid_power_factor():

    with pytest.raises(ValueError):

        calculate_electrical_load(
            connected_load_kw=100,
            demand_factor=0.8,
            diversity_factor=1.2,
            power_factor=0,
            voltage=400,
            phase="Three Phase",
        )


def test_invalid_diversity_factor():

    with pytest.raises(ValueError):

        calculate_electrical_load(
            connected_load_kw=100,
            demand_factor=0.8,
            diversity_factor=0.8,
            power_factor=0.9,
            voltage=400,
            phase="Three Phase",
        )
