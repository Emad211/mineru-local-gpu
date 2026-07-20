"""Generate a small medical-style test PDF (text + a dosing table) to smoke-test MinerU."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("test_sample.pdf", pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
story = []
story.append(Paragraph("Hypertension Management — MinerU Test Document", styles["Title"]))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph(
    "Hypertension is a common chronic condition. First-line pharmacologic options include "
    "calcium channel blockers, ACE inhibitors, and thiazide diuretics. The table below "
    "summarizes typical oral starting and maximum daily doses for selected agents in adults.",
    styles["BodyText"]))
story.append(Spacer(1, 0.5*cm))

data = [
    ["Drug", "Class", "Starting Dose", "Max Daily Dose"],
    ["Amlodipine", "CCB", "5 mg once daily", "10 mg"],
    ["Lisinopril", "ACE inhibitor", "10 mg once daily", "40 mg"],
    ["Hydrochlorothiazide", "Thiazide", "12.5 mg once daily", "50 mg"],
    ["Losartan", "ARB", "50 mg once daily", "100 mg"],
]
t = Table(data, colWidths=[4*cm, 3.5*cm, 4*cm, 3.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f2f2f2")]),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
]))
story.append(t)
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "Note: Doses are illustrative for software testing only and must not be used clinically.",
    styles["Italic"]))

doc.build(story)
print("Created test_sample.pdf")
