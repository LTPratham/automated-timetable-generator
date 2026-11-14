"""Export timetable schedules to printable PDF documents."""

from io import BytesIO
from typing import Dict
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from src.models.entities import SessionVariable, SlotAssignment, SessionType
from src.models.dataset import DepartmentDataset


def export_timetable_to_pdf(
    dataset: DepartmentDataset,
    assignment: Dict[SessionVariable, SlotAssignment],
) -> BytesIO:
    """Generates a landscape, presentation-ready PDF of student and faculty schedules."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1F497D"),
        alignment=1,  # Center
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=1,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        alignment=1,
    )
    header_cell_style = ParagraphStyle(
        "HeaderCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,
    )

    elements = []
    days = dataset.days
    num_slots = min(dataset.daily_slots_count, len(dataset.slot_times))

    for b_idx, batch in enumerate(dataset.batches):
        if b_idx > 0:
            elements.append(PageBreak())

        # Title block
        elements.append(Paragraph(f"Academic Timetable — {dataset.name}", title_style))
        elements.append(Paragraph(f"<b>Batch:</b> {batch.name} | <b>Enrolled Strength:</b> {batch.strength}", subtitle_style))
        elements.append(Spacer(1, 15))

        # Build timetable matrix data
        header_row = [Paragraph("<b>Day / Time</b>", header_cell_style)]
        for s_idx in range(num_slots):
            t_start, t_end = dataset.slot_times[s_idx]
            header_row.append(Paragraph(f"<b>Slot {s_idx + 1}</b><br/>{t_start}-{t_end}", header_cell_style))

        table_data = [header_row]

        # Populate rows
        for day in days:
            row = [Paragraph(f"<b>{day.value}</b>", cell_style)]
            for slot_idx in range(num_slots):
                # Find matching session
                matching_entry = None
                for var, assign in assignment.items():
                    if var.batch_id == batch.id and assign.day == day:
                        if assign.start_slot_index <= slot_idx < assign.start_slot_index + assign.duration_slots:
                            matching_entry = (var, assign)
                            break

                if matching_entry:
                    var, assign = matching_entry
                    fac = dataset.faculty_by_id.get(var.faculty_id)
                    fac_name = fac.name.split()[-1] if fac else var.faculty_id
                    room = dataset.rooms_by_id.get(assign.room_id)
                    room_name = room.name if room else assign.room_id
                    type_tag = "[LAB]" if var.session_type == SessionType.LAB else "[TH]"
                    cell_text = f"<b>{var.course_code} {type_tag}</b><br/>{room_name}<br/>Prof. {fac_name}"
                    row.append(Paragraph(cell_text, cell_style))
                else:
                    row.append(Paragraph("-", cell_style))

            table_data.append(row)

        col_widths = [75] + [110] * num_slots
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F497D")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0B0B0")),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#E9EEF4")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(t)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    buffer.seek(0)
    return buffer

