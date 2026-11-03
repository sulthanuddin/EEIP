from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]
REFERENCE_ROOT = PROJECT_ROOT / "data" / "reference_data"

AMPACITY_FILE = REFERENCE_ROOT / "cables" / "ampacity.csv"
IMPEDANCE_FILE = REFERENCE_ROOT / "cables" / "impedance.csv"
PROTECTION_FILE = REFERENCE_ROOT / "protection" / "devices.csv"


AMPACITY_COLUMNS = [
    "record_id", "material", "insulation", "reference_method",
    "construction", "loaded_conductors", "area_mm2", "ampacity_a",
    "reference_ambient_c", "source", "source_edition", "verified",
]

IMPEDANCE_COLUMNS = [
    "record_id", "material", "insulation", "construction",
    "area_mm2", "resistance_ohm_km_20c",
    "reactance_ohm_km", "source", "verified",
]

PROTECTION_COLUMNS = [
    "device_id", "device_type", "rated_current_a", "i2_factor",
    "manufacturer", "model", "source", "verified",
]


def load_reference_file(path, required_columns):
    if not path.exists():
        raise FileNotFoundError(
            f"Reference database not found: {path}"
        )

    df = pd.read_csv(path, dtype=str)

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing database columns: {sorted(missing)}"
        )

    if df.empty:
        return df

    return df


def load_ampacity_database():
    return load_reference_file(AMPACITY_FILE, AMPACITY_COLUMNS)


def load_impedance_database():
    return load_reference_file(IMPEDANCE_FILE, IMPEDANCE_COLUMNS)


def load_protection_database():
    return load_reference_file(PROTECTION_FILE, PROTECTION_COLUMNS)


def _validate_identifiers(df, id_column, description):
    values = df[id_column].fillna("").astype(str).str.strip()

    if values.eq("").any():
        raise ValueError(
            f"{description} database contains a missing {id_column}."
        )

    if values.duplicated().any():
        duplicates = values[values.duplicated(keep=False)].tolist()
        raise ValueError(
            f"Duplicate {description} identifiers: {duplicates}"
        )

    df[id_column] = values


def _validate_sources(df, source_columns, description):
    for column in source_columns:
        values = df[column].fillna("").astype(str).str.strip()

        if values.eq("").any():
            raise ValueError(
                f"Verified {description} records require "
                f"a non-empty {column}."
            )

        df[column] = values


def _verified_rows(df, description):
    if df.empty:
        return df.copy()

    raw = df["verified"].fillna("").astype(str).str.strip().str.lower()

    allowed = {"true", "false"}
    invalid = ~raw.isin(allowed)

    if invalid.any():
        bad_values = raw[invalid].unique().tolist()
        raise ValueError(
            f"{description} database contains invalid verification "
            f"flags: {bad_values}. Use true or false."
        )

    result = df.copy()
    result["verified"] = raw.eq("true")

    return result[result["verified"]].copy()


def _numeric_columns(df, columns, description):
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[columns].isna().any().any():
        invalid_columns = [
            column for column in columns
            if df[column].isna().any()
        ]
        raise ValueError(
            f"Verified {description} records contain invalid numeric "
            f"values in: {invalid_columns}"
        )


def _validate_unique_configuration(df, columns, description):
    if df.empty:
        return

    if df[columns].isna().any().any():
        raise ValueError(
            f"Verified {description} records contain missing "
            f"configuration fields."
        )

    duplicates = df.duplicated(subset=columns, keep=False)

    if duplicates.any():
        duplicate_records = df.loc[
            duplicates, columns
        ].to_dict("records")

        raise ValueError(
            f"Duplicate verified {description} configurations: "
            f"{duplicate_records}"
        )


def verified_ampacity_records():
    df = load_ampacity_database()

    _validate_identifiers(df, "record_id", "ampacity")
    df = _verified_rows(df, "ampacity")

    if df.empty:
        return df

    _validate_sources(
        df, ["source", "source_edition"], "ampacity"
    )

    numeric = [
        "loaded_conductors",
        "area_mm2",
        "ampacity_a",
        "reference_ambient_c",
    ]
    _numeric_columns(df, numeric, "ampacity")

    if (
        (df["loaded_conductors"] <= 0).any()
        or (df["area_mm2"] <= 0).any()
        or (df["ampacity_a"] <= 0).any()
    ):
        raise ValueError(
            "Ampacity, cable area and loaded conductors "
            "must be positive."
        )

    _validate_unique_configuration(
        df,
        [
            "material", "insulation", "reference_method",
            "construction", "loaded_conductors", "area_mm2",
        ],
        "ampacity",
    )

    return df


def verified_impedance_records():
    df = load_impedance_database()

    _validate_identifiers(df, "record_id", "impedance")
    df = _verified_rows(df, "impedance")

    if df.empty:
        return df

    _validate_sources(df, ["source"], "impedance")

    numeric = [
        "area_mm2",
        "resistance_ohm_km_20c",
        "reactance_ohm_km",
    ]
    _numeric_columns(df, numeric, "impedance")

    if (
        (df["area_mm2"] <= 0).any()
        or (df["resistance_ohm_km_20c"] <= 0).any()
        or (df["reactance_ohm_km"] < 0).any()
    ):
        raise ValueError(
            "Invalid impedance data: area and resistance must "
            "be positive; reactance cannot be negative."
        )

    _validate_unique_configuration(
        df,
        ["material", "insulation", "construction", "area_mm2"],
        "impedance",
    )

    return df


def verified_protection_records():
    df = load_protection_database()

    _validate_identifiers(df, "device_id", "protection")
    df = _verified_rows(df, "protection")

    if df.empty:
        return df

    _validate_sources(df, ["source"], "protection")

    for column in ("device_type", "manufacturer", "model"):
        values = df[column].fillna("").astype(str).str.strip()

        if values.eq("").any():
            raise ValueError(
                f"Verified protection records require {column}."
            )

        df[column] = values

    numeric = ["rated_current_a", "i2_factor"]
    _numeric_columns(df, numeric, "protection")

    if (
        (df["rated_current_a"] <= 0).any()
        or (df["i2_factor"] <= 0).any()
    ):
        raise ValueError(
            "Protective-device rated current and I2 factor "
            "must be positive."
        )

    return df