import pandas as pd
import pytest

from app.modules.electrical_design.cable_sizing import cable_database


@pytest.fixture
def valid_ampacity():
    return pd.DataFrame([{
        "record_id": "AMP-001",
        "material": "Copper",
        "insulation": "XLPE",
        "reference_method": "C",
        "construction": "Multicore",
        "loaded_conductors": 3,
        "area_mm2": 16,
        "ampacity_a": 80,
        "reference_ambient_c": 30,
        "source": "TEST SOURCE",
        "source_edition": "TEST EDITION",
        "verified": "true",
    }])


@pytest.fixture
def valid_impedance():
    return pd.DataFrame([{
        "record_id": "IMP-001",
        "material": "Copper",
        "insulation": "XLPE",
        "construction": "Multicore",
        "area_mm2": 16,
        "resistance_ohm_km_20c": 1.15,
        "reactance_ohm_km": 0.08,
        "source": "TEST SOURCE",
        "verified": "true",
    }])


@pytest.fixture
def valid_protection():
    return pd.DataFrame([{
        "device_id": "CB-001",
        "device_type": "MCB",
        "rated_current_a": 50,
        "i2_factor": 1.45,
        "manufacturer": "TEST MANUFACTURER",
        "model": "TEST MODEL",
        "source": "TEST SOURCE",
        "verified": "true",
    }])


def test_duplicate_ampacity_record_id_rejected(
    valid_ampacity, monkeypatch
):
    duplicate = pd.concat(
        [valid_ampacity, valid_ampacity],
        ignore_index=True,
    )

    monkeypatch.setattr(
        cable_database,
        "load_ampacity_database",
        lambda: duplicate.copy(),
    )

    with pytest.raises(ValueError, match="Duplicate ampacity identifiers"):
        cable_database.verified_ampacity_records()


def test_missing_verified_ampacity_source_rejected(
    valid_ampacity, monkeypatch
):
    valid_ampacity.loc[0, "source"] = ""

    monkeypatch.setattr(
        cable_database,
        "load_ampacity_database",
        lambda: valid_ampacity.copy(),
    )

    with pytest.raises(ValueError, match="source"):
        cable_database.verified_ampacity_records()


def test_invalid_verification_flag_rejected(
    valid_impedance, monkeypatch
):
    valid_impedance.loc[0, "verified"] = "maybe"

    monkeypatch.setattr(
        cable_database,
        "load_impedance_database",
        lambda: valid_impedance.copy(),
    )

    with pytest.raises(ValueError, match="invalid verification flags"):
        cable_database.verified_impedance_records()


def test_missing_protection_manufacturer_rejected(
    valid_protection, monkeypatch
):
    valid_protection.loc[0, "manufacturer"] = ""

    monkeypatch.setattr(
        cable_database,
        "load_protection_database",
        lambda: valid_protection.copy(),
    )

    with pytest.raises(ValueError, match="manufacturer"):
        cable_database.verified_protection_records()