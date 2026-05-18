"""Script temporaire — génère un PDF de test avec règle 1 respectée."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

OUT = Path("../assets/sample_base_first/regle1_conforme.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

doc = SimpleDocTemplate(str(OUT), pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Relevé bancaire — Calcul de saisie", styles["Heading2"]))
elements.append(Spacer(1, 0.5*cm))

data = [
    ["Libellé", "Montant"],
    ["Solde du compte", "1 250.00 EUR"],
    ["Solde bancaire insaisissable à retenir", "0.59 EUR"],
    ["Total saisissable", "0.30 EUR"],
]

table = Table(data, colWidths=[11*cm, 5*cm])
table.setStyle(TableStyle([
    # En-tête
    ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#1e293b")),
    ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
    ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",     (0, 0), (-1, 0), 10),
    # Corps
    ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE",     (0, 1), (-1, -1), 9),
    ("BACKGROUND",   (0, 2), (-1, 2), colors.HexColor("#eff6ff")),  # insaisissable
    ("BACKGROUND",   (0, 3), (-1, 3), colors.HexColor("#f0fdf4")),  # saisissable
    # Grille (nécessaire pour Camelot lattice)
    ("GRID",         (0, 0), (-1, -1), 0.75, colors.HexColor("#94a3b8")),
    ("BOX",          (0, 0), (-1, -1), 1.5,  colors.HexColor("#1e293b")),
    # Alignement
    ("ALIGN",        (1, 0), (1, -1), "RIGHT"),
    ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING",   (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ("LEFTPADDING",  (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
]))

elements.append(table)
doc.build(elements)
print(f"PDF généré : {OUT}")
