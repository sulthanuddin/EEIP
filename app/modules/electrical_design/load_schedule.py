
import math
from collections import defaultdict


VALID_PHASES = {"Single Phase", "Three Phase"}


def validate_equipment(item):
    """Validate one equipment schedule record."""

    required = [
        "equipment",
        "distribution_board",
        "quantity",
        "unit_kw",
        "demand_factor",
        "power_factor",
        "phase",
        "voltage",
    ]

    for field in required:
        if field not in item:
            raise ValueError(f"Missing field: {field}")

    if not str(item["equipment"]).strip():
        raise ValueError("Equipment name cannot be empty.")

    if not str(item["distribution_board"]).strip():
        raise ValueError("Distribution board cannot be empty.")

    if isinstance(item["quantity"], bool) or not isinstance(
        item["quantity"], int
    ) or item["quantity"] <= 0:
        raise ValueError("Quantity must be a positive integer.")

    numeric_fields = [
        "unit_kw",
        "demand_factor",
        "power_factor",
        "voltage",
    ]

    for field in numeric_fields:
        value = item[field]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be numeric.")

        if not math.isfinite(value):
            raise ValueError(f"{field} must be finite.")

    if item["unit_kw"] <= 0:
        raise ValueError("Unit load must be greater than zero.")

    if not 0 < item["demand_factor"] <= 1:
        raise ValueError("Demand factor must be greater than 0 and at most 1.")

    if not 0 < item["power_factor"] <= 1:
        raise ValueError("Power factor must be greater than 0 and at most 1.")

    if item["voltage"] <= 0:
        raise ValueError("Voltage must be greater than zero.")

    if item["phase"] not in VALID_PHASES:
        raise ValueError("Invalid supply configuration.")


def calculate_load_schedule(equipment_list, diversity_by_db=None):
    """
    Calculate equipment-wise loads and distribution-board summaries.

    Assumptions:
    - Unit load is electrical input power in kW.
    - Demand factor applies to each equipment group.
    - Distribution-board diversity factor applies to the
      aggregate active and reactive demand.
    - Loads within one DB use the same nominal voltage and phase system.
    - Balanced three-phase current is assumed.
    """

    if not equipment_list:
        raise ValueError("Add at least one equipment item.")

    diversity_by_db = diversity_by_db or {}

    equipment_results = []
    groups = defaultdict(list)

    for item in equipment_list:
        validate_equipment(item)

        db = item["distribution_board"].strip()

        connected_kw = item["quantity"] * item["unit_kw"]

        demand_kw = connected_kw * item["demand_factor"]

        reactive_kvar = demand_kw * math.tan(
            math.acos(item["power_factor"])
        )

        calculated_item = {
            **item,
            "distribution_board": db,
            "connected_kw": connected_kw,
            "demand_kw": demand_kw,
            "reactive_kvar": reactive_kvar,
        }

        equipment_results.append(calculated_item)
        groups[db].append(calculated_item)

    db_results = []

    for db, items in groups.items():

        voltages = {item["voltage"] for item in items}
        phases = {item["phase"] for item in items}

        if len(voltages) != 1:
            raise ValueError(
                f"{db}: All items must use the same nominal voltage."
            )

        if len(phases) != 1:
            raise ValueError(
                f"{db}: Mixed phase systems are not supported in one DB."
            )

        voltage = items[0]["voltage"]
        phase = items[0]["phase"]

        diversity_factor = diversity_by_db.get(db, 1.0)

        if (
            isinstance(diversity_factor, bool)
            or not isinstance(diversity_factor, (int, float))
            or not math.isfinite(diversity_factor)
            or diversity_factor < 1
        ):
            raise ValueError(
                f"{db}: Diversity factor must be finite and at least 1."
            )

        connected_kw = sum(
            item["connected_kw"] for item in items
        )

        individual_demand_kw = sum(
            item["demand_kw"] for item in items
        )

        individual_reactive_kvar = sum(
            item["reactive_kvar"] for item in items
        )

        # Apply the DB coincidence/diversity assumption
        maximum_demand_kw = (
            individual_demand_kw / diversity_factor
        )

        maximum_reactive_kvar = (
            individual_reactive_kvar / diversity_factor
        )

        apparent_power_kva = math.sqrt(
            maximum_demand_kw ** 2
            + maximum_reactive_kvar ** 2
        )

        if apparent_power_kva == 0:
            effective_pf = 1.0
        else:
            effective_pf = (
                maximum_demand_kw / apparent_power_kva
            )

        if phase == "Three Phase":
            current_a = (
                apparent_power_kva * 1000
                / (math.sqrt(3) * voltage)
            )
        else:
            current_a = apparent_power_kva * 1000 / voltage

        db_results.append({
            "distribution_board": db,
            "phase": phase,
            "voltage": voltage,
            "connected_kw": connected_kw,
            "individual_demand_kw": individual_demand_kw,
            "maximum_demand_kw": maximum_demand_kw,
            "reactive_kvar": maximum_reactive_kvar,
            "apparent_power_kva": apparent_power_kva,
            "effective_power_factor": effective_pf,
            "diversity_factor": diversity_factor,
            "current_a": current_a,
            "equipment_count": len(items),
        })

    return {
        "equipment": equipment_results,
        "distribution_boards": db_results,
        "totals": {
            "connected_kw": sum(
                db["connected_kw"] for db in db_results
            ),
            "maximum_demand_kw": sum(
                db["maximum_demand_kw"] for db in db_results
            ),
            "apparent_power_kva": sum(
                db["apparent_power_kva"] for db in db_results
            ),
        },
    }
