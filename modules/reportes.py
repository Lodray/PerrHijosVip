# modules/reportes.py
import os
import csv
import calendar
from datetime import datetime, timedelta
from modules.utils import ruta_reports_dir, ruta_registros, parse_datetime_try as _parse_date_try
from modules import extras as extras_mod

try:
    import pandas as pd
    PANDAS = True
except:
    PANDAS = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    REPORTLAB = True
except:
    REPORTLAB = False

def _parse_date_try_local(s):
    if not s: return None
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], fmt if len(fmt) <= len(s) else "%Y-%m-%d")
        except:
            continue
    try:
        return datetime.fromisoformat(s)
    except:
        return None

def generar_reporte_range(start_date:str, end_date:str, salida_excel=True, salida_pdf=True):
    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except Exception as e:
        return {"error": f"Fechas inválidas: {e}"}

    # leer registros
    regs = []
    p_regs = ruta_registros()
    if os.path.exists(p_regs):
        with open(p_regs, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                regs.append(r)
    regs_map = { r.get("ID"): r for r in regs }

    # --- NOCHES / GUARDERIA (solo registros 'pagado') ---
    noches_rows = []
    ingresos_noches = 0.0
    count_nights = 0
    for r in regs:
        estado = (r.get("EstadoPago") or "").strip().lower()
        if estado != "pagado":
            continue
        servicio = (r.get("Servicio") or "").strip().lower() or "estancia"
        try:
            cantidad = int(float(r.get("Cantidad") or 1))
            if cantidad < 1: cantidad = 1
        except:
            cantidad = 1

        if servicio == "guarderia":
            try:
                durmins = int(float(r.get("DurationMinutes") or 0))
            except:
                durmins = 0
            try:
                precio_hora = float(r.get("PrecioPorNoche") or 0.0)
            except:
                precio_hora = 0.0
            horas = max(0.0, durmins / 60.0)
            importe_unidad = round(precio_hora * horas, 2)
            importe_total = round(importe_unidad * cantidad, 2)
            fi = _parse_date_try_local((r.get("FechaIngreso") or "")[:19])
            if not fi:
                continue
            atrib_date = fi.date()
            if sd <= atrib_date <= ed:
                noches_rows.append({
                    "Tipo": "GUARDERIA",
                    "ID": r.get("ID"),
                    "Nombre": (r.get("Nombre") or "")[:30],
                    "Fecha": atrib_date.strftime("%Y-%m-%d"),
                    "Concepto": f"Guardería {horas:.2f}h x {cantidad}",
                    "Importe": f"{importe_total:.2f}"
                })
                ingresos_noches += importe_total
                count_nights += 1
        else:
            fi = _parse_date_try_local((r.get("FechaIngreso") or "")[:19])
            try:
                noches = int(float(r.get("Noches") or 0))
            except:
                noches = 0
            if not fi or noches <= 0:
                continue
            precio_unitario = float(r.get("PrecioPorNoche") or 0.0)
            for i in range(max(0, noches)):
                noche_inicio_date = (fi + timedelta(days=i)).date()
                year = noche_inicio_date.year; month = noche_inicio_date.month; day = noche_inicio_date.day
                last_day = calendar.monthrange(year, month)[1]
                atrib_date = noche_inicio_date
                if day == last_day:
                    atrib_date = noche_inicio_date + timedelta(days=1)
                if sd <= atrib_date <= ed:
                    importe = round(precio_unitario * cantidad, 2)
                    noches_rows.append({
                        "Tipo": "NOCHE",
                        "ID": r.get("ID"),
                        "Nombre": (r.get("Nombre") or "")[:30],
                        "Fecha": atrib_date.strftime("%Y-%m-%d"),
                        "Concepto": "Precio por noche",
                        "Importe": f"{importe:.2f}"
                    })
                    ingresos_noches += importe
                    count_nights += 1

    # --- EXTRAS: leer extras.csv en rango (rango extendido sd-1 .. ed para reatribucion) ---
    extras_rows = []
    ingresos_extras = 0.0
    count_extras = 0
    rango_inicio = (sd - timedelta(days=1)).strftime("%Y-%m-%d")
    rango_fin = ed.strftime("%Y-%m-%d")
    extra_list = extras_mod.extras_en_rango(rango_inicio, rango_fin)

    # construir mapa de sumas de extras desde extras.csv (por registro)
    extras_csv_by_reg = {}
    independent_extras = []
    for ex in extra_list:
        fecha_ex_str = (ex.get("Fecha") or "")[:10]
        if not fecha_ex_str:
            continue
        try:
            fecha_ex_dt = datetime.strptime(fecha_ex_str, "%Y-%m-%d").date()
        except:
            continue
        registro_id = (ex.get("RegistroID") or ex.get("registro_id") or "").strip() or None
        # omitimos huérfanos (registro no existe)
        if registro_id and registro_id not in regs_map:
            continue
        # calcular atrib_date
        atrib_date = fecha_ex_dt
        if registro_id and registro_id in regs_map:
            reg = regs_map[registro_id]
            fi = _parse_date_try_local((reg.get("FechaIngreso") or "")[:19])
            fs = _parse_date_try_local((reg.get("FechaSalida") or "")[:19])
            if not fs and fi:
                try:
                    noches = int(float(reg.get("Noches") or 0))
                except:
                    noches = 0
                fs = fi + timedelta(days=noches)
            if fi:
                year = fecha_ex_dt.year; month = fecha_ex_dt.month; day = fecha_ex_dt.day
                last_day = calendar.monthrange(year, month)[1]
                if day == last_day and fs and fs.date() > fecha_ex_dt:
                    atrib_date = fecha_ex_dt + timedelta(days=1)
        if not (sd <= atrib_date <= ed):
            continue
        try:
            monto = float(ex.get("Monto") or ex.get("monto") or 0.0)
        except:
            monto = 0.0
        if registro_id:
            extras_csv_by_reg.setdefault(registro_id, 0.0)
            extras_csv_by_reg[registro_id] += monto
        else:
            independent_extras.append({
                "Tipo": "EXTRA",
                "ID": ex.get("ID"),
                "RegistroID": "",
                "Nombre": "",
                "Fecha": atrib_date.strftime("%Y-%m-%d"),
                "Concepto": ex.get("Nota") or ex.get("nota") or "Extra",
                "Importe": f"{monto:.2f}"
            })
            ingresos_extras += monto
            count_extras += 1

    # Ahora combinamos: para cada registro, decidimos usar extras_csv_by_reg (si hay)
    # o usar reg["Extras"] si NO hay entradas en extras.csv para ese registro.
    for rid, reg in regs_map.items():
        estado_reg = (reg.get("EstadoPago") or "").strip().lower()
        # suma de extras según origen
        csv_sum = round(extras_csv_by_reg.get(rid, 0.0), 2)
        try:
            reg_extras_base = round(float(reg.get("Extras") or 0.0), 2)
        except:
            reg_extras_base = 0.0
        # Preferir CSV cuando hay registros detallados; si no, usar el valor en el registro
        extras_sum_a_usar = csv_sum if csv_sum > 0 else reg_extras_base

        if estado_reg == "pagado":
            if extras_sum_a_usar > 0:
                extras_rows.append({
                    "Tipo": "EXTRA",
                    "ID": f"EXTRA_SUM_{rid}",
                    "RegistroID": rid,
                    "Nombre": "",
                    "Fecha": (reg.get("FechaIngreso") or "")[:10],
                    "Concepto": f"Extras (Registro {rid})",
                    "Importe": f"{extras_sum_a_usar:.2f}"
                })
                ingresos_extras += extras_sum_a_usar
                count_extras += 1
        # si estado anticipo/cancelado -> será sumado al anticipo más abajo
        # si estado vacío -> nada

    # añadir extras independientes (ya sumadas)
    extras_rows = extras_rows + independent_extras

    # --- ANTICIPOS: incluir anticipo SOLO para registros en estado 'anticipo' o 'cancelado'
    anticipos_rows = []
    ingresos_anticipos = 0.0
    count_anticipos = 0
    for r in regs:
        estado = (r.get("EstadoPago") or "").strip().lower()
        try:
            fecha_ing = (r.get("FechaIngreso") or "")[:10]
            fecha_dt = datetime.strptime(fecha_ing, "%Y-%m-%d").date()
        except Exception:
            continue
        try:
            antic = float(r.get("Anticipo") or 0.0)
        except:
            antic = 0.0
        if estado in ("anticipo", "cancelado"):
            # sumar extras asociados: preferir CSV si existe, sino el valor en registro
            csv_sum = round(extras_csv_by_reg.get(r.get("ID"), 0.0), 2)
            try:
                reg_extras_base = round(float(r.get("Extras") or 0.0), 2)
            except:
                reg_extras_base = 0.0
            extra_sum = csv_sum if csv_sum > 0 else reg_extras_base
            total_anticpo_a_sumar = round(antic + extra_sum, 2)
            if sd <= fecha_dt <= ed and total_anticpo_a_sumar > 0:
                anticipos_rows.append({
                    "Tipo": "ANTICIPO",
                    "ID": r.get("ID"),
                    "Nombre": (r.get("Nombre") or "")[:30],
                    "Fecha": fecha_dt.strftime("%Y-%m-%d"),
                    "Concepto": "Anticipo" + (" (+extras)" if extra_sum>0 else ""),
                    "Importe": f"{total_anticpo_a_sumar:.2f}"
                })
                ingresos_anticipos += total_anticpo_a_sumar
                count_anticipos += 1

    # combinar filas (primero noches/guarderia, luego extras, luego anticipos)
    rows_out = noches_rows + extras_rows + anticipos_rows
    total_ingresos = round(ingresos_noches + ingresos_extras + ingresos_anticipos, 2)

    out = {
        "start": start_date,
        "end": end_date,
        "count_nights": count_nights,
        "count_extras": count_extras,
        "count_anticipos": count_anticipos,
        "total_ingresos": total_ingresos,
        "total_extras": round(ingresos_extras, 2),
        "total_noches": round(ingresos_noches, 2),
        "total_anticipos": round(ingresos_anticipos, 2),
        "rows": rows_out
    }

    reports_dir = ruta_reports_dir(); os.makedirs(reports_dir, exist_ok=True)

    # EXCEL / CSV
    if salida_excel and PANDAS:
        df = pd.DataFrame(rows_out)
        xfile = os.path.join(reports_dir, f"reporte_{start_date}_to_{end_date}.xlsx")
        df.to_excel(xfile, index=False); out["excel"] = xfile
    elif salida_excel:
        xfile = os.path.join(reports_dir, f"reporte_{start_date}_to_{end_date}.csv")
        with open(xfile, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tipo","ID","RegistroID","Nombre","Fecha","Concepto","Importe"])
            for r in rows_out:
                writer.writerow([r.get("Tipo",""), r.get("ID",""), r.get("RegistroID",""), r.get("Nombre",""), r.get("Fecha",""), r.get("Concepto",""), r.get("Importe","")])
        out["csv"] = xfile

    # PDF
    if salida_pdf and REPORTLAB:
        pfile = os.path.join(reports_dir, f"reporte_{start_date}_to_{end_date}.pdf")
        c = canvas.Canvas(pfile, pagesize=letter)
        width, height = letter
        margin = 1.5 * cm
        y = height - 2 * cm

        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, f"Reporte PerrHijosVIP {start_date} → {end_date}")
        y -= 0.7 * cm
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, f"Noches: {len(noches_rows)}   Extras: {len(extras_rows)}   Anticipos: {len(anticipos_rows)}   Total: ${total_ingresos:.2f}")
        y -= 0.8 * cm

        headers = ["Fecha", "Tipo", "Concepto", "Nombre/ID", "Importe"]
        col_widths = [3.0, 2.0, 6.0, 6.0, 3.0]  # cm
        x_positions = [margin + sum(col_widths[:i]) * cm for i in range(len(col_widths))]

        c.setFont("Helvetica-Bold", 9)
        for i, h in enumerate(headers):
            c.drawString(x_positions[i], y, h)
        y -= 0.4 * cm
        c.setFont("Helvetica", 8)

        for row in rows_out:
            if y < 2 * cm:
                c.showPage()
                c.setFont("Helvetica", 8)
                y = height - 2 * cm
            fecha = row.get("Fecha", "")
            tipo = row.get("Tipo", "")
            concepto = (row.get("Concepto", "") or "")[:40]
            nombre = (row.get("Nombre", "") or row.get("RegistroID", "") or "")[:30]
            importe = f"${row.get('Importe', '0')}"
            vals = [fecha, tipo, concepto, nombre, importe]
            for i, v in enumerate(vals):
                c.drawString(x_positions[i], y, str(v))
            y -= 0.35 * cm

        y -= 0.5 * cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, f"Total general: ${total_ingresos:.2f}")
        c.save()
        out["pdf"] = pfile

    return out
