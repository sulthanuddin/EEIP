import math

from app.modules.electrical_design.cable_sizing.cable_database import (
    verified_ampacity_records,
    verified_impedance_records,
    verified_protection_records,
)

from app.modules.electrical_design.cable_sizing.voltage_drop import (
    calculate_design_current,
    calculate_voltage_drop,
    correct_resistance_for_temperature,
)


STANDARD_CABLE_SIZES = [
    1.5, 2.5, 4, 6, 10, 16, 25, 35,
    50, 70, 95, 120, 150, 185, 240,
    300, 400, 500, 630,
]

SUPPORTED_METHODS = [
    "A1", "A2", "B1", "B2",
    "C", "D1", "D2", "E", "F", "G",
]


def validate_cable_inputs(data):
    required = [
        "power_kw", "voltage_v", "power_factor", "efficiency",
        "phase", "material", "insulation", "reference_method",
        "construction", "loaded_conductors", "length_m",
        "ambient_factor", "grouping_factor", "other_factor",
        "voltage_drop_limit_percent", "operating_temperature_c",
        "short_circuit_current_a", "fault_clearing_time_s", "k_factor",
    ]

    for field in required:
        if field not in data:
            raise ValueError(f"Missing input: {field}")

        if data[field] is None:
            raise ValueError(f"{field} cannot be empty.")

        if isinstance(data[field], bool):
            raise ValueError(f"{field} cannot be Boolean.")

    # Validate text/enumeration fields separately.
    text_fields = {
        "phase": ("Single Phase", "Three Phase"),
        "material": ("Copper", "Aluminium"),
        "insulation": ("XLPE", "PVC"),
        "reference_method": tuple(SUPPORTED_METHODS),
        "construction": ("Single Core", "Multicore"),
    }

    for field, allowed_values in text_fields.items():
        if data[field] not in allowed_values:
            raise ValueError(
                f"Invalid {field}: {data[field]}. "
                f"Allowed values: {allowed_values}"
            )

    # Validate numeric fields only.
    numeric_fields = [
        "power_kw", "voltage_v", "power_factor", "efficiency",
        "loaded_conductors", "length_m", "ambient_factor",
        "grouping_factor", "other_factor",
        "voltage_drop_limit_percent", "operating_temperature_c",
        "short_circuit_current_a", "fault_clearing_time_s", "k_factor",
    ]

    for field in numeric_fields:
        try:
            value = float(data[field])
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be numeric.")

        if not math.isfinite(value):
            raise ValueError(f"{field} must be finite.")

    if int(float(data["loaded_conductors"])) != float(
        data["loaded_conductors"]
    ):
        raise ValueError("Loaded conductors must be an integer.")

    if int(float(data["loaded_conductors"])) not in (2, 3):
        raise ValueError("Loaded conductors must be 2 or 3.")

    positive_fields = [
        "power_kw", "voltage_v", "efficiency", "length_m",
        "voltage_drop_limit_percent", "fault_clearing_time_s",
        "short_circuit_current_a", "k_factor",
    ]

    for field in positive_fields:
        if float(data[field]) <= 0:
            raise ValueError(f"{field} must be greater than zero.")

    if not 0 < float(data["power_factor"]) <= 1:
        raise ValueError("Power factor must be between 0 and 1.")

    if float(data["efficiency"]) > 1:
        raise ValueError("Efficiency must not exceed 1.0.")

    for field in ("ambient_factor", "grouping_factor", "other_factor"):
        if not 0 < float(data[field]) <= 1:
            raise ValueError(
                f"{field} must be greater than 0 and at most 1."
            )

def _require_unique_records(df, key_columns, description):
    if df.empty:
        raise ValueError(f"No verified {description} records are available.")

    if df[key_columns].isna().any().any():
        raise ValueError(f"{description} records contain missing key values.")

    duplicates = df.duplicated(subset=key_columns, keep=False)

    if duplicates.any():
        keys = df.loc[duplicates, key_columns].to_dict("records")
        raise ValueError(
            f"Ambiguous duplicate {description} records: {keys}"
        )


def select_cable(data):
    """
    Evaluate cable/protective-device combinations.

    Implemented checks:
      - Ib <= In <= Iz
      - I2 <= 1.45 x Iz
      - Voltage drop <= project limit
      - Adiabatic short-circuit withstand

    This is a preliminary selection engine. Final design approval also
    requires verification of device breaking capacity, disconnection
    times, earth-fault protection, installation conditions and applicable
    manufacturer/IEC data.
    """
    validate_cable_inputs(data)

    ib = calculate_design_current(
        power_kw=float(data["power_kw"]),
        voltage_v=float(data["voltage_v"]),
        power_factor=float(data["power_factor"]),
        phase=data["phase"],
        efficiency=float(data["efficiency"]),
    )

    ampacity_df = verified_ampacity_records().copy()
    impedance_df = verified_impedance_records().copy()
    protection_df = verified_protection_records().copy()

    ampacity_df = ampacity_df[
        (ampacity_df["material"] == data["material"])
        & (ampacity_df["insulation"] == data["insulation"])
        & (ampacity_df["reference_method"] == data["reference_method"])
        & (ampacity_df["construction"] == data["construction"])
        & (
            ampacity_df["loaded_conductors"]
            == data["loaded_conductors"]
        )
    ].copy()

    impedance_df = impedance_df[
        (impedance_df["material"] == data["material"])
        & (impedance_df["insulation"] == data["insulation"])
        & (impedance_df["construction"] == data["construction"])
    ].copy()

    if ampacity_df.empty:
        raise ValueError(
            "No verified ampacity records match the selected cable configuration."
        )

    if impedance_df.empty:
        raise ValueError(
            "No verified cable impedance records match the selected configuration."
        )

    if protection_df.empty:
        raise ValueError("No verified protective-device records are available.")

    _require_unique_records(
        ampacity_df, ["area_mm2"], "matching ampacity"
    )
    _require_unique_records(
        impedance_df, ["area_mm2"], "matching impedance"
    )
    _require_unique_records(
        protection_df, ["device_id"], "protective-device"
    )

    protection_df = protection_df[
        protection_df["rated_current_a"] >= ib
    ].sort_values(["rated_current_a", "device_id"])

    if protection_df.empty:
        raise ValueError(
            "No verified protective device has a rated current at or above design current."
        )

    correction_factor = (
        float(data["ambient_factor"])
        * float(data["grouping_factor"])
        * float(data["other_factor"])
    )

    ampacity_by_area = ampacity_df.set_index("area_mm2")
    impedance_by_area = impedance_df.set_index("area_mm2")

    candidates = []

    for area in sorted(STANDARD_CABLE_SIZES):
        if area not in ampacity_by_area.index:
            continue

        if area not in impedance_by_area.index:
            continue

        ampacity_record = ampacity_by_area.loc[area]
        impedance_record = impedance_by_area.loc[area]

        reference_ampacity = float(ampacity_record["ampacity_a"])
        corrected_ampacity = reference_ampacity * correction_factor

        resistance = correct_resistance_for_temperature(
            float(impedance_record["resistance_ohm_km_20c"]),
            float(data["operating_temperature_c"]),
            data["material"],
        )

        reactance = float(impedance_record["reactance_ohm_km"])

        voltage_result = calculate_voltage_drop(
            current_a=ib,
            length_m=float(data["length_m"]),
            voltage_v=float(data["voltage_v"]),
            power_factor=float(data["power_factor"]),
            resistance_ohm_km=resistance,
            reactance_ohm_km=reactance,
            phase=data["phase"],
        )

        voltage_ok = (
            voltage_result["voltage_drop_percent"]
            <= float(data["voltage_drop_limit_percent"])
        )

        short_circuit_required_area = (
            float(data["short_circuit_current_a"])
            * math.sqrt(float(data["fault_clearing_time_s"]))
            / float(data["k_factor"])
        )

        short_circuit_ok = area >= short_circuit_required_area

        # Evaluate every eligible protective device for this cable size.
        for _, protection in protection_df.iterrows():
            in_a = float(protection["rated_current_a"])
            i2_factor = float(protection["i2_factor"])

            overload_ok = (
                ib <= in_a
                and in_a <= corrected_ampacity
                and i2_factor * in_a <= 1.45 * corrected_ampacity
            )

            candidates.append({
                "area_mm2": area,
                "reference_ampacity_a": reference_ampacity,
                "corrected_ampacity_a": corrected_ampacity,
                "design_current_a": ib,
                "protective_device_a": in_a,
                "protection_device_id": protection["device_id"],
                "protection_device_type": protection["device_type"],
                "protection_manufacturer": protection["manufacturer"],
                "protection_model": protection["model"],
                "protection_i2_factor": i2_factor,
                "voltage_drop_v": voltage_result["voltage_drop_v"],
                "voltage_drop_percent": voltage_result[
                    "voltage_drop_percent"
                ],
                "resistance_ohm_km": resistance,
                "reactance_ohm_km": reactance,
                "short_circuit_required_area_mm2": (
                    short_circuit_required_area
                ),
                "overload_ok": overload_ok,
                "voltage_ok": voltage_ok,
                "short_circuit_ok": short_circuit_ok,
                "overall_ok": (
                    overload_ok and voltage_ok and short_circuit_ok
                ),
                "ampacity_record_id": ampacity_record["record_id"],
                "impedance_record_id": impedance_record["record_id"],
            })

    if not candidates:
        raise ValueError(
            "No matching cable sizes exist in the verified reference database."
        )

    passing = [
        item for item in candidates if item["overall_ok"]
    ]

    if not passing:
        return {
            "status": "NO_SUITABLE_CABLE",
            "design_current_a": ib,
            "protective_device_a": None,
            "selected_cable": None,
            "candidates": candidates,
            "message": (
                "No cable and protective-device combination satisfies "
                "all implemented checks."
            ),
        }

    # Minimum cross-section first; lowest valid device rating breaks ties.
    selected = min(
        passing,
        key=lambda item: (
            item["area_mm2"],
            item["protective_device_a"],
        ),
    )

    return {
        "status": "PASS",
        "design_current_a": ib,
        "protective_device_a": selected["protective_device_a"],
        "correction_factor": correction_factor,
        "selected_cable": selected,
        "candidates": candidates,
        "message": (
            "A cable and protective-device combination satisfies "
            "the implemented checks."
        ),
    }