
from io import BytesIO

import pandas as pd

from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def build_equipment_dataframe(results):
    """Create an equipment-wise report table."""

    columns = [
        "equipment",
        "distribution_board",
        "quantity",
        "unit_kw",
        "connected_kw",
        "demand_factor",
        "demand_kw",
        "power_factor",
        "reactive_kvar",
        "phase",
        "voltage",
    ]

    return pd.DataFrame(
        results["equipment"],
        columns=columns
    )


def build_db_dataframe(results):
    """Create a distribution-board summary table."""

    return pd.DataFrame(results["distribution_boards"])


def generate_excel_report(results, project_name):
    """Generate a formatted Excel workbook in memory."""

    equipment_df = build_equipment_dataframe(results)
    db_df = build_db_dataframe(results)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        equipment_df.to_excel(
            writer,
            sheet_name="Equipment Schedule",
            index=False
        )

        db_df.to_excel(
            writer,
            sheet_name="DB Summary",
            index=False
        )

        workbook = writer.book

        for worksheet in workbook.worksheets:

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

            for cell in worksheet[1]:

                cell.font = Font(
                    bold=True,
                    color="FFFFFF"
                )

                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor="17365D"
                )

                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center"
                )

            for column in worksheet.columns:

                column_letter = column[0].column_letter

                max_length = max(
                    len(str(cell.value or ""))
                    for cell in column
                )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(max(max_length + 3, 12), 32)

            for row in worksheet.iter_rows(min_row=2):

                for cell in row:
                    cell.alignment = Alignment(
                        vertical="center"
                    )

        info = workbook.create_sheet("Project Information", 0)

        info.append(["EEIP - Electrical Load Schedule"])
        info.append(["Project", project_name])
        info.append(["Report Type", "Equipment-wise Load Schedule"])
        info.append(["Design Basis", "IEC-oriented preliminary calculation"])
        info.append(["Connected Load (kW)", results["totals"]["connected_kw"]])
        info.append(["Maximum Demand (kW)", results["totals"]["maximum_demand_kw"]])
        info.append([
            "Sum of DB Apparent Powers (kVA)",
            results["totals"]["apparent_power_kva"]
        ])
        info.append([
            "Important",
            "Preliminary engineering results. Independent design verification required."
        ])

        info["A1"].font = Font(
            bold=True,
            size=16,
            color="FFFFFF"
        )

        info["A1"].fill = PatternFill(
            fill_type="solid",
            fgColor="17365D"
        )

        info.column_dimensions["A"].width = 38
        info.column_dimensions["B"].width = 85

        info.freeze_panes = "A2"

    output.seek(0)

    return output.getvalue()


def generate_pdf_report(results, project_name):
    """Generate a landscape PDF load schedule."""

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "EEIP - Electrical Load Schedule",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"Project: {project_name}",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "Design basis: IEC-oriented preliminary engineering calculation",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 6 * mm))

    totals = results["totals"]

    summary_data = [
        ["Connected Load", "Maximum Demand", "Sum of DB kVA"],
        [
            f'{totals["connected_kw"]:.2f} kW',
            f'{totals["maximum_demand_kw"]:.2f} kW',
            f'{totals["apparent_power_kva"]:.2f} kVA',
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[85 * mm, 85 * mm, 85 * mm]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 7 * mm))

    story.append(
        Paragraph(
            "Equipment-wise Schedule",
            styles["Heading2"]
        )
    )

    headers = [
        "Equipment",
        "DB",
        "Qty",
        "Unit kW",
        "Connected kW",
        "DF",
        "Demand kW",
        "PF",
        "Phase",
        "Voltage",
    ]

    table_data = [headers]

    for item in results["equipment"]:

        table_data.append([
            str(item["equipment"]),
            str(item["distribution_board"]),
            str(item["quantity"]),
            f'{item["unit_kw"]:.2f}',
            f'{item["connected_kw"]:.2f}',
            f'{item["demand_factor"]:.2f}',
            f'{item["demand_kw"]:.2f}',
            f'{item["power_factor"]:.2f}',
            str(item["phase"]),
            f'{item["voltage"]:.0f} V',
        ])

    equipment_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            42 * mm,
            22 * mm,
            12 * mm,
            19 * mm,
            24 * mm,
            12 * mm,
            22 * mm,
            12 * mm,
            25 * mm,
            20 * mm,
        ],
    )

    equipment_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#EAF0F6"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    story.append(equipment_table)
    story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            "Distribution Board Summary",
            styles["Heading2"]
        )
    )

    db_data = [[
        "Distribution Board",
        "Phase",
        "Voltage",
        "Connected kW",
        "Maximum Demand kW",
        "Reactive kVAr",
        "Apparent kVA",
        "Effective PF",
        "Diversity Factor",
        "Current A",
    ]]

    for db in results["distribution_boards"]:

        db_data.append([
            db["distribution_board"],
            db["phase"],
            f'{db["voltage"]:.0f}',
            f'{db["connected_kw"]:.2f}',
            f'{db["maximum_demand_kw"]:.2f}',
            f'{db["reactive_kvar"]:.2f}',
            f'{db["apparent_power_kva"]:.2f}',
            f'{db["effective_power_factor"]:.3f}',
            f'{db["diversity_factor"]:.2f}',
            f'{db["current_a"]:.2f}',
        ])

    db_table = Table(
        db_data,
        repeatRows=1,
        colWidths=[
            30 * mm, 23 * mm, 17 * mm, 23 * mm, 29 * mm,
            23 * mm, 23 * mm, 20 * mm, 25 * mm, 20 * mm,
        ],
    )

    db_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    story.append(db_table)
    story.append(Spacer(1, 7 * mm))

    story.append(
        Paragraph(
            "<b>Engineering disclaimer:</b> "
            "This report contains preliminary calculations. "
            "Verify load characteristics, diversity assumptions, "
            "phase allocation, harmonics, protection, cable sizing "
            "and applicable project standards before design approval.",
            styles["Normal"]
        )
    )

    document.build(story)

    output.seek(0)

    return output.getvalue()
