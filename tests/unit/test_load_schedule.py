from io import BytesIO
from openpyxl import load_workbook
from pypdf import PdfReader

from app.modules.electrical_design.schedule_reports import (
    generate_excel_report,
    generate_pdf_report,
)
import pytest

from app.modules.electrical_design.load_schedule import (
    calculate_load_schedule,
)


@pytest.fixture
def sample_equipment():

    return [
        {
            "equipment": "Water Pump",
            "distribution_board": "DB-M01",
            "quantity": 2,
            "unit_kw": 10.0,
            "demand_factor": 0.8,
            "power_factor": 0.8,
            "phase": "Three Phase",
            "voltage": 400.0,
        },
    ]


def test_connected_load(sample_equipment):

    result = calculate_load_schedule(sample_equipment)

    assert result["totals"]["connected_kw"] == pytest.approx(20.0)


def test_individual_demand(sample_equipment):

    result = calculate_load_schedule(sample_equipment)

    assert result["equipment"][0]["demand_kw"] == pytest.approx(16.0)


def test_db_diversity_calculation(sample_equipment):

    result = calculate_load_schedule(
        sample_equipment,
        {"DB-M01": 2.0},
    )

    db = result["distribution_boards"][0]

    assert db["maximum_demand_kw"] == pytest.approx(8.0)
    assert db["reactive_kvar"] == pytest.approx(6.0)
    assert db["apparent_power_kva"] == pytest.approx(10.0)
    assert db["effective_power_factor"] == pytest.approx(0.8)


def test_three_phase_current(sample_equipment):

    result = calculate_load_schedule(
        sample_equipment,
        {"DB-M01": 2.0},
    )

    current = result["distribution_boards"][0]["current_a"]

    assert current == pytest.approx(14.43376, abs=0.001)


def test_empty_schedule_rejected():

    with pytest.raises(ValueError):
        calculate_load_schedule([])


def test_invalid_demand_factor(sample_equipment):

    sample_equipment[0]["demand_factor"] = 1.5

    with pytest.raises(ValueError):
        calculate_load_schedule(sample_equipment)


def test_mixed_voltage_in_same_db_rejected(sample_equipment):

    second_item = sample_equipment[0].copy()

    second_item["equipment"] = "Lighting"
    second_item["voltage"] = 230.0

    with pytest.raises(ValueError):
        calculate_load_schedule(
            sample_equipment + [second_item]
        )


def test_invalid_diversity_rejected(sample_equipment):

    with pytest.raises(ValueError):
        calculate_load_schedule(
            sample_equipment,
            {"DB-M01": 0.8},
        )




def test_excel_report_generation(sample_equipment):

    results = calculate_load_schedule(sample_equipment)

    excel_bytes = generate_excel_report(
        results,
        "Test Commercial Building",
    )

    workbook = load_workbook(BytesIO(excel_bytes))

    assert "Project Information" in workbook.sheetnames
    assert "Equipment Schedule" in workbook.sheetnames
    assert "DB Summary" in workbook.sheetnames

    worksheet = workbook["Equipment Schedule"]

    assert worksheet.max_row == 2
    assert worksheet["A2"].value == "Water Pump"


def test_pdf_report_generation(sample_equipment):

    results = calculate_load_schedule(sample_equipment)

    pdf_bytes = generate_pdf_report(
        results,
        "Test Commercial Building",
    )

    assert pdf_bytes.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_bytes))

    assert len(reader.pages) >= 1

    extracted_text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    assert "Electrical Load Schedule" in extracted_text
    assert "Water Pump" in extracted_text
    assert "Test Commercial Building" in extracted_text
