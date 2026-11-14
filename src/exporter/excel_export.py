"""Export timetable schedules to formatted Excel workbooks."""

from io import BytesIO
from typing import Dict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from src.models.entities import SessionVariable, SlotAssignment, SessionType
from src.models.dataset import DepartmentDataset


def export_timetable_to_excel(
    dataset: DepartmentDataset,
    assignment: Dict[SessionVariable, SlotAssignment],
) -> BytesIO:
    """Creates a stylized multi-sheet Excel workbook of the generated timetable."""
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    day_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    theory_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    lab_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="B0B0B0"),
        right=Side(style="thin", color="B0B0B0"),
        top=Side(style="thin", color="B0B0B0"),
        bottom=Side(style="thin", color="B0B0B0"),
    )

    days = dataset.days
    num_slots = min(dataset.daily_slots_count, len(dataset.slot_times))
    slot_labels = [f"Slot {i+1}\n({dataset.slot_times[i][0]}-{dataset.slot_times[i][1]})" for i in range(num_slots)]

    # --- 1. Sheet for each Student Batch ---
    for batch in dataset.batches:
        ws = wb.create_sheet(title=f"Batch {batch.id[:20]}")
        ws.views.sheetView[0].showGridLines = True

        # Title
        ws.merge_cells("A1:G1")
        title_cell = ws["A1"]
        title_cell.value = f"Academic Timetable — {batch.name} (Capacity: {batch.strength})"
        title_cell.font = Font(name="Calibri", size=14, bold=True, color="1F497D")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30

        # Header row (Slots)
        ws.cell(row=3, column=1, value="Day / Time").font = header_font
        ws.cell(row=3, column=1).fill = header_fill
        ws.cell(row=3, column=1).alignment = Alignment(horizontal="center", vertical="center")

        for s_idx, label in enumerate(slot_labels):
            cell = ws.cell(row=3, column=s_idx + 2, value=label)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws.row_dimensions[3].height = 28

        # Day rows
        for d_idx, day in enumerate(days):
            row_num = d_idx + 4
            ws.row_dimensions[row_num].height = 45
            day_cell = ws.cell(row=row_num, column=1, value=day.value)
            day_cell.font = Font(name="Calibri", size=11, bold=True)
            day_cell.fill = day_fill
            day_cell.alignment = Alignment(horizontal="center", vertical="center")
            day_cell.border = thin_border

            # Fill empty slot cells
            for s_idx in range(num_slots):
                cell = ws.cell(row=row_num, column=s_idx + 2, value="-")
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

        # Populate batch assignments
        for var, assign in assignment.items():
            if var.batch_id == batch.id:
                d_idx = days.index(assign.day)
                row_num = d_idx + 4
                fac = dataset.faculty_by_id.get(var.faculty_id)
                fac_name = fac.name if fac else var.faculty_id
                room = dataset.rooms_by_id.get(assign.room_id)
                room_name = room.name if room else assign.room_id

                content = f"{var.course_code}: {var.course_title}\n[{room_name}] — {fac_name}"

                for slot_offset in range(assign.duration_slots):
                    col_num = assign.start_slot_index + slot_offset + 2
                    if col_num <= num_slots + 1:
                        cell = ws.cell(row=row_num, column=col_num, value=content)
                        cell.fill = lab_fill if var.session_type == SessionType.LAB else theory_fill
                        cell.font = Font(name="Calibri", size=9, bold=(slot_offset == 0))
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        cell.border = thin_border

        # Column widths
        ws.column_dimensions["A"].width = 15
        for col_letter in ["B", "C", "D", "E", "F", "G"]:
            ws.column_dimensions[col_letter].width = 24

    # Save to memory buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

