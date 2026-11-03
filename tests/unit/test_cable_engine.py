
import pandas as pd
import pytest

from app.modules.electrical_design.cable_sizing import cable_engine


@pytest.fixture
def cable_inputs():
    return {
        "power_kw": 30.0,
        "voltage_v": 400.0,
        "power_factor": 0.9,
        "efficiency": 1.0,
        "phase": "Three Phase",
        "material": "Copper",
        "insulation": "XLPE",
        "reference_method": "C",
        "construction": "Multicore",
        "loaded_conductors": 3,
        "length_m": 50.0,
        "ambient_factor": 1.0,
        "grouping_factor": 1.0,
        "other_factor": 1.0,
        "voltage_drop_limit_percent": 3.0,
        "operating_temperature_c": 90.0,
        "short_circuit_current_a": 5000.0,
        "fault_clearing_time_s": 0.2,
        "k_factor": 143.0,
    }


@pytest.fixture
def reference_data():
    ampacity = pd.DataFrame([
        {
            "record_id": "TEST-A16",
            "material": "Copper",
            "insulation": "XLPE",
            "reference_method": "C",
            "construction": "Multicore",
            "loaded_conductors": 3,
            "area_mm2": 16,
            "ampacity_a": 80,
            "reference_ambient_c": 30,
            "source": "TEST FIXTURE",
            "source_edition": "TEST",
            "verified": True,
        },
        {
            "record_id": "TEST-A25",
            "material": "Copper",
            "insulation": "XLPE",
            "reference_method": "C",
            "construction": "Multicore",
            "loaded_conductors": 3,
            "area_mm2": 25,
            "ampacity_a": 100,
            "reference_ambient_c": 30,
            "source": "TEST FIXTURE",
            "source_edition": "TEST",
            "verified": True,
        },
    ])

    impedance = pd.DataFrame([
        {
            "record_id": "TEST-Z16",
            "material": "Copper",
            "insulation": "XLPE",
            "construction": "Multicore",
            "area_mm2": 16,
            "resistance_ohm_km_20c": 1.15,
            "reactance_ohm_km": 0.08,
            "source": "TEST FIXTURE",
            "verified": True,
        },
        {
            "record_id": "TEST-Z25",
            "material": "Copper",
            "insulation": "XLPE",
            "construction": "Multicore",
            "area_mm2": 25,
            "resistance_ohm_km_20c": 0.727,
            "reactance_ohm_km": 0.08,
            "source": "TEST FIXTURE",
            "verified": True,
        },
    ])

    protection = pd.DataFrame([
        {
            "device_id": "TEST-MCB-50",
            "device_type": "MCB",
            "rated_current_a": 50,
            "i2_factor": 1.45,
            "manufacturer": "TEST",
            "model": "TEST-50",
            "source": "TEST FIXTURE",
            "verified": True,
        },
    ])

    return ampacity, impedance, protection


def install_test_database(monkeypatch, reference_data):
    ampacity, impedance, protection = reference_data

    monkeypatch.setattr(
        cable_engine,
        "verified_ampacity_records",
        lambda: ampacity.copy(),
    )
    monkeypatch.setattr(
        cable_engine,
        "verified_impedance_records",
        lambda: impedance.copy(),
    )
    monkeypatch.setattr(
        cable_engine,
        "verified_protection_records",
        lambda: protection.copy(),
    )


# Original six tests

def test_cable_selection_passes(cable_inputs, reference_data, monkeypatch):
    install_test_database(monkeypatch, reference_data)

    result = cable_engine.select_cable(cable_inputs)

    assert result["status"] == "PASS"
    assert result["selected_cable"]["area_mm2"] == 16


def test_cable_selection_rejects_invalid_material(cable_inputs):
    cable_inputs["material"] = "Steel"

    with pytest.raises(ValueError):
        cable_engine.select_cable(cable_inputs)


def test_invalid_correction_factor(cable_inputs):
    cable_inputs["ambient_factor"] = 1.5

    with pytest.raises(ValueError):
        cable_engine.select_cable(cable_inputs)


def test_no_matching_database_records(cable_inputs, reference_data, monkeypatch):
    install_test_database(monkeypatch, reference_data)
    cable_inputs["material"] = "Aluminium"

    with pytest.raises(ValueError, match="No verified ampacity"):
        cable_engine.select_cable(cable_inputs)


def test_no_suitable_cable(cable_inputs, reference_data, monkeypatch):
    install_test_database(monkeypatch, reference_data)
    cable_inputs["voltage_drop_limit_percent"] = 0.01

    result = cable_engine.select_cable(cable_inputs)

    assert result["status"] == "NO_SUITABLE_CABLE"


def test_short_circuit_check(cable_inputs, reference_data, monkeypatch):
    install_test_database(monkeypatch, reference_data)
    cable_inputs["short_circuit_current_a"] = 100000

    result = cable_engine.select_cable(cable_inputs)

    assert result["status"] == "NO_SUITABLE_CABLE"


# New protective-device selection tests

def test_selects_lowest_valid_protective_device(
    cable_inputs, reference_data, monkeypatch
):
    ampacity, impedance, protection = reference_data

    additional_device = pd.DataFrame([{
        "device_id": "TEST-MCB-63",
        "device_type": "MCB",
        "rated_current_a": 63,
        "i2_factor": 1.45,
        "manufacturer": "TEST",
        "model": "TEST-63",
        "source": "TEST FIXTURE",
        "verified": True,
    }])

    protection = pd.concat(
        [protection, additional_device],
        ignore_index=True,
    )

    install_test_database(
        monkeypatch, (ampacity, impedance, protection)
    )

    result = cable_engine.select_cable(cable_inputs)

    assert result["status"] == "PASS"
    assert result["protective_device_a"] == 50
    assert result["selected_cable"]["protection_device_id"] == "TEST-MCB-50"


def test_tries_next_device_when_first_fails_coordination(
    cable_inputs, reference_data, monkeypatch
):
    ampacity, impedance, protection = reference_data

    protection.loc[0, "i2_factor"] = 3.0

    additional_device = pd.DataFrame([{
        "device_id": "TEST-MCB-63",
        "device_type": "MCB",
        "rated_current_a": 63,
        "i2_factor": 1.45,
        "manufacturer": "TEST",
        "model": "TEST-63",
        "source": "TEST FIXTURE",
        "verified": True,
    }])

    protection = pd.concat(
        [protection, additional_device],
        ignore_index=True,
    )

    install_test_database(
        monkeypatch, (ampacity, impedance, protection)
    )

    result = cable_engine.select_cable(cable_inputs)

    assert result["status"] == "PASS"
    assert result["protective_device_a"] == 63
    assert result["selected_cable"]["protection_device_id"] == "TEST-MCB-63"


def test_no_protective_device_combination_passes(
    cable_inputs, reference_data, monkeypatch
):
    ampacity, impedance, protection = reference_data

    protection.loc[0, "i2_factor"] = 3.0

    install_test_database(
        monkeypatch, (ampacity, impedance, protection)
    )

    result = cable_engine.select_cable(cable_inputs)

    assert result["status"] == "NO_SUITABLE_CABLE"
    assert result["selected_cable"] is None


def test_duplicate_ampacity_configuration_rejected(
    cable_inputs, reference_data, monkeypatch
):
    ampacity, impedance, protection = reference_data

    ampacity = pd.concat(
        [ampacity, ampacity.iloc[[0]]],
        ignore_index=True,
    )

    install_test_database(
        monkeypatch, (ampacity, impedance, protection)
    )

    with pytest.raises(ValueError, match="duplicate"):
        cable_engine.select_cable(cable_inputs)


def test_duplicate_impedance_configuration_rejected(
    cable_inputs, reference_data, monkeypatch
):
    ampacity, impedance, protection = reference_data

    impedance = pd.concat(
        [impedance, impedance.iloc[[0]]],
        ignore_index=True,
    )

    install_test_database(
        monkeypatch, (ampacity, impedance, protection)
    )

    with pytest.raises(ValueError, match="duplicate"):
        cable_engine.select_cable(cable_inputs)
