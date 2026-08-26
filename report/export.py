"""Esportazione dei report in CSV e PDF: stesso contenuto della pagina a schermo,
solo per fascicolo (commercialista, federazione, archivio esterno...)."""

import csv
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def genera_csv(dati):
    """Restituisce il contenuto CSV (stringa) con tutte le sezioni del report."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([f"Report EquiLesson — dal {dati['dal']:%d/%m/%Y} al {dati['al']:%d/%m/%Y}"])
    writer.writerow([])

    writer.writerow(["Presenze/assenze per allievo"])
    writer.writerow(["Allievo", "Svolte", "Assenti", "%"])
    for r in dati["presenze"]:
        writer.writerow([
            f"{r['allievo__nome']} {r['allievo__cognome']}", r["svolte"], r["assenti"],
            r["percentuale"] if r["percentuale"] is not None else "",
        ])
    writer.writerow([])

    writer.writerow(["Utilizzo cavalli"])
    writer.writerow(["Cavallo", "Lezioni"])
    for r in dati["utilizzo_cavalli"]:
        writer.writerow([r["cavallo__nome"], r["numero_lezioni"]])
    writer.writerow([])

    writer.writerow(["Occupazione istruttori"])
    writer.writerow(["Istruttore", "Lezioni"])
    for r in dati["occupazione_istruttori"]:
        writer.writerow([f"{r['istruttore__nome']} {r['istruttore__cognome']}", r["numero_lezioni"]])
    writer.writerow([])

    writer.writerow(["Occupazione campi"])
    writer.writerow(["Campo", "Lezioni"])
    for r in dati["occupazione_campi"]:
        writer.writerow([r["campo__nome"], r["numero_lezioni"]])
    writer.writerow([])

    writer.writerow(["Allievi in scadenza (prossimi 30 giorni)"])
    writer.writerow(["Allievo", "Tipo", "Scadenza", "Stato"])
    for v in dati["scadenze"]:
        writer.writerow([
            str(v["allievo"]), v["tipo"], v["scadenza"].strftime("%d/%m/%Y"),
            "Scaduto" if v["scaduto"] else "In scadenza",
        ])
    writer.writerow([])

    writer.writerow(["Cavalli: scadenze sanitarie (prossimi 30 giorni)"])
    writer.writerow(["Cavallo", "Tipo", "Scadenza", "Stato"])
    for v in dati["scadenze_cavalli"]:
        writer.writerow([
            str(v["cavallo"]), v["tipo"], v["scadenza"].strftime("%d/%m/%Y"),
            "Scaduto" if v["scaduto"] else "In scadenza",
        ])

    return buffer.getvalue()


def _tabella(intestazioni, righe, stili):
    if not righe:
        righe = [["Nessun dato nel periodo."] + [""] * (len(intestazioni) - 1)]
    dati_tabella = [intestazioni] + righe
    tabella = Table(dati_tabella, hAlign="LEFT")
    tabella.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    return tabella


def genera_pdf(dati):
    """Restituisce il contenuto PDF (bytes) con tutte le sezioni del report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
    )
    stili = getSampleStyleSheet()
    elementi = [
        Paragraph("Report EquiLesson", stili["Title"]),
        Paragraph(f"Dal {dati['dal']:%d/%m/%Y} al {dati['al']:%d/%m/%Y}", stili["Normal"]),
        Spacer(1, 0.5 * cm),
    ]

    elementi.append(Paragraph("Presenze/assenze per allievo", stili["Heading2"]))
    righe = [
        [f"{r['allievo__nome']} {r['allievo__cognome']}", str(r["svolte"]), str(r["assenti"]),
         f"{r['percentuale']}%" if r["percentuale"] is not None else "—"]
        for r in dati["presenze"]
    ]
    elementi.append(_tabella(["Allievo", "Svolte", "Assenti", "%"], righe, stili))
    elementi.append(Spacer(1, 0.5 * cm))

    elementi.append(Paragraph("Utilizzo cavalli", stili["Heading2"]))
    righe = [[r["cavallo__nome"], str(r["numero_lezioni"])] for r in dati["utilizzo_cavalli"]]
    elementi.append(_tabella(["Cavallo", "Lezioni"], righe, stili))
    elementi.append(Spacer(1, 0.5 * cm))

    elementi.append(Paragraph("Occupazione istruttori", stili["Heading2"]))
    righe = [
        [f"{r['istruttore__nome']} {r['istruttore__cognome']}", str(r["numero_lezioni"])]
        for r in dati["occupazione_istruttori"]
    ]
    elementi.append(_tabella(["Istruttore", "Lezioni"], righe, stili))
    elementi.append(Spacer(1, 0.5 * cm))

    elementi.append(Paragraph("Occupazione campi", stili["Heading2"]))
    righe = [[r["campo__nome"], str(r["numero_lezioni"])] for r in dati["occupazione_campi"]]
    elementi.append(_tabella(["Campo", "Lezioni"], righe, stili))
    elementi.append(Spacer(1, 0.5 * cm))

    elementi.append(Paragraph("Allievi in scadenza (prossimi 30 giorni)", stili["Heading2"]))
    righe = [
        [str(v["allievo"]), v["tipo"], v["scadenza"].strftime("%d/%m/%Y"), "Scaduto" if v["scaduto"] else "In scadenza"]
        for v in dati["scadenze"]
    ]
    elementi.append(_tabella(["Allievo", "Tipo", "Scadenza", "Stato"], righe, stili))
    elementi.append(Spacer(1, 0.5 * cm))

    elementi.append(Paragraph("Cavalli: scadenze sanitarie (prossimi 30 giorni)", stili["Heading2"]))
    righe = [
        [str(v["cavallo"]), v["tipo"], v["scadenza"].strftime("%d/%m/%Y"), "Scaduto" if v["scaduto"] else "In scadenza"]
        for v in dati["scadenze_cavalli"]
    ]
    elementi.append(_tabella(["Cavallo", "Tipo", "Scadenza", "Stato"], righe, stili))

    doc.build(elementi)
    return buffer.getvalue()
