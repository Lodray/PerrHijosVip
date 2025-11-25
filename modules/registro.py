# === FILE: modules/registro.py ===
import os
import csv
import shutil
from datetime import datetime, timedelta
from modules.utils import ruta_registros, generar_id, parse_datetime_try as utils_parse_dt_try
from modules import extras as extras_mod

# HEADERS: añadidos Cantidad, Servicio, EstadoPago, DurationMinutes
HEADERS = ["ID","Nombre","Cantidad","Noches","PrecioPorNoche","Extras","Total","Anticipo","Restante","FechaIngreso","FechaSalida","EstadoPago","Servicio","DurationMinutes"]

def asegurar_csv():
    p = ruta_registros()
    carpeta = os.path.dirname(p)
    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta, exist_ok=True)
    if not os.path.exists(p):
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
    else:
        # comprobar cabecera
        with open(p, "r", newline="", encoding="utf-8") as f:
            first_line = f.readline().strip()
        first = [c.strip() for c in first_line.split(",")] if first_line else []
        if not first or any(h not in first for h in HEADERS):
            normalizar_csv_existente()

def encabezados_actuales():
    p = ruta_registros()
    if not os.path.exists(p):
        return []
    with open(p, "r", newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        try:
            first = next(r)
            return [c.strip() for c in first]
        except StopIteration:
            return []

def normalizar_csv_existente():
    p = ruta_registros()
    if not os.path.exists(p):
        return {"ok": True, "msg": "No existe archivo."}
    bk = p + ".bak"
    try:
        shutil.copy(p, bk)
    except Exception:
        bk = None

    reconstructed = []
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    if not reader:
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
        return {"ok": True, "msg": "Archivo vacío, creado header."}

    first = reader[0]
    first_lower = [c.lower().strip() for c in first]
    headers_lower = [h.lower() for h in HEADERS]
    has_header = any(h in first_lower for h in headers_lower)

    if has_header:
        with open(p, "r", newline="", encoding="utf-8") as f:
            dr = csv.DictReader(f)
            for r in dr:
                rec = {k: (r.get(k, "") if r.get(k, "") is not None else "") for k in HEADERS}
                if not rec.get("FechaSalida"):
                    fi = (rec.get("FechaIngreso") or "")[:19]
                    try:
                        base = utils_parse_dt_try(fi)
                        noches = int(float(rec.get("Noches") or 0))
                        fs = base + timedelta(days=noches)
                        rec["FechaSalida"] = fs.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        rec["FechaSalida"] = ""
                reconstructed.append(rec)
    else:
        for row in reader:
            if not row:
                continue
            cols = row + [""] * (len(HEADERS) - len(row))
            cols = cols[:len(HEADERS)]
            rec = dict(zip(HEADERS, cols))
            if not rec.get("FechaSalida"):
                fi = (rec.get("FechaIngreso") or "")[:19]
                try:
                    base = utils_parse_dt_try(fi)
                    noches = int(float(rec.get("Noches") or 0))
                    fs = base + timedelta(days=noches)
                    rec["FechaSalida"] = fs.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    rec["FechaSalida"] = ""
            reconstructed.append(rec)

    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(reconstructed)

    return {"ok": True, "msg": f"Normalizados {len(reconstructed)} filas.", "backup": bk}

# parse helper
def _parse_dt_try(s):
    if not s: return None
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], fmt if len(fmt)<=len(s) else "%Y-%m-%d")
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s)
    except:
        return None

def calcular_fecha_salida_dt(fecha_ingreso_str, noches):
    base = _parse_dt_try(fecha_ingreso_str)
    if not base:
        base = datetime.now()
    try:
        n = int(float(noches))
    except:
        n = 1
    return base + timedelta(days=n)

def agregar_registro(nombre, noches:int, precio_por_noche:float, extras_total:float, anticipo_pct:float, fecha_ingreso=None, cantidad=1, servicio="Estancia", estado_pago="Anticipo", duration_minutes=None):
    asegurar_csv()
    try:
        noches_i = int(noches)
    except:
        noches_i = 0
    precio_f = float(precio_por_noche)
    extras_f = float(extras_total or 0.0)

    # calcular total diferente si es guarderia
    if (servicio or "").lower() == "guarderia":
        dur = int(duration_minutes or 0)
        hours = max(0.0, dur / 60.0)
        total = round(hours * precio_f * int(cantidad or 1) + extras_f, 2)
        noches_i = 0
    else:
        total = round(int(cantidad or 1) * noches_i * precio_f + extras_f, 2)

    anticipo = round(total * (float(anticipo_pct) / 100.0), 2)
    restante = round(total - anticipo, 2)

    if fecha_ingreso is None or fecha_ingreso == "":
        fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        if len(fecha_ingreso) == 10:
            fecha_ingreso = fecha_ingreso + " 00:00:00"
        elif len(fecha_ingreso) == 16:
            fecha_ingreso = fecha_ingreso + ":00"

    fs_dt = calcular_fecha_salida_dt(fecha_ingreso, noches_i)
    fecha_salida_str = fs_dt.strftime("%Y-%m-%d %H:%M:%S")

    nid = generar_id()
    p = ruta_registros()
    row = {
        "ID": nid,
        "Nombre": nombre,
        "Cantidad": str(cantidad or 1),
        "Noches": str(noches_i),
        "PrecioPorNoche": f"{precio_f:.2f}",
        "Extras": f"{extras_f:.2f}",
        "Total": f"{total:.2f}",
        "Anticipo": f"{anticipo:.2f}",
        "Restante": f"{restante:.2f}",
        "FechaIngreso": fecha_ingreso,
        "FechaSalida": fecha_salida_str,
        "EstadoPago": estado_pago,
        "Servicio": servicio,
        "DurationMinutes": str(duration_minutes or "")
    }

    current_headers = encabezados_actuales()
    if not current_headers or any(h not in current_headers for h in HEADERS):
        normalizar_csv_existente()

    with open(p, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if os.path.getsize(p) == 0:
            writer.writeheader()
        writer.writerow(row)
    return nid

def leer_registros():
    asegurar_csv()
    p = ruta_registros()
    rows = []
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rec = {k: (r.get(k, "") if r.get(k, "") is not None else "") for k in HEADERS}
            if not rec.get("FechaSalida"):
                fi = (rec.get("FechaIngreso") or "")[:19]
                try:
                    base = _parse_dt_try(fi)
                    noches = int(float(rec.get("Noches") or 0))
                    fs = base + timedelta(days=noches)
                    rec["FechaSalida"] = fs.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    rec["FechaSalida"] = ""
            rows.append(rec)
    return rows

def buscar_registros_por_nombre(term):
    term = (term or "").strip().lower()
    if not term:
        return leer_registros()
    return [r for r in leer_registros() if term in (r.get("Nombre") or "").lower()]

def eliminar_por_id(rec_id):
    p = ruta_registros()
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    nuevas = [r for r in reader if r.get("ID") != rec_id]
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(nuevas)
    # eliminar extras asociados
    try:
        extras_mod.eliminar_extras_por_registro(rec_id)
    except Exception:
        pass
    return True

def actualizar_registro(rec_id, nombre, noches, extras, precio_por_noche, anticipo_pct, fecha_ingreso=None, cantidad=None, servicio=None, estado_pago=None, duration_minutes=None):
    p = ruta_registros()
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    changed = False
    for r in reader:
        if r.get("ID") == rec_id:
            try:
                old_extras = float(r.get("Extras") or 0.0)
            except:
                old_extras = 0.0
            try:
                new_extras = float(extras or 0.0)
            except:
                new_extras = old_extras

            noches_i = int(noches)
            precio_f = float(precio_por_noche)
            # cantidad
            cantidad_i = int(cantidad) if cantidad is not None else int(r.get("Cantidad") or 1)
            serv = servicio if servicio is not None else r.get("Servicio") or "Estancia"
            if (serv or "").lower() == "guarderia":
                dur = int(duration_minutes or r.get("DurationMinutes") or 0)
                hours = max(0.0, dur/60.0)
                total = round(hours * precio_f * cantidad_i + new_extras, 2)
                r["Noches"] = "0"
            else:
                total = round(cantidad_i * noches_i * precio_f + new_extras, 2)
                r["Noches"] = str(noches_i)

            anticipo = round(total * (float(anticipo_pct) / 100.0), 2)
            restante = round(total - anticipo, 2)

            r["Nombre"] = nombre
            r["Cantidad"] = str(cantidad_i)
            r["PrecioPorNoche"] = f"{precio_f:.2f}"
            r["Extras"] = f"{new_extras:.2f}"
            r["Total"] = f"{total:.2f}"
            r["Anticipo"] = f"{anticipo:.2f}"
            r["Restante"] = f"{restante:.2f}"
            if fecha_ingreso is not None:
                if len(fecha_ingreso) == 10:
                    fecha_ingreso = fecha_ingreso + " 00:00:00"
                elif len(fecha_ingreso) == 16:
                    fecha_ingreso = fecha_ingreso + ":00"
                r["FechaIngreso"] = fecha_ingreso
                fs_dt = calcular_fecha_salida_dt(fecha_ingreso, noches_i)
                r["FechaSalida"] = fs_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                fi = (r.get("FechaIngreso") or "")[:19]
                try:
                    fs_dt = calcular_fecha_salida_dt(fi, noches_i)
                    r["FechaSalida"] = fs_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass

            if duration_minutes is not None:
                r["DurationMinutes"] = str(duration_minutes)
            if servicio is not None:
                r["Servicio"] = servicio
            if estado_pago is not None:
                r["EstadoPago"] = estado_pago

            diff = round(new_extras - old_extras, 2)
            if diff > 0:
                try:
                    extras_mod.agregar_extra(rec_id, diff, fecha=datetime.now().strftime("%Y-%m-%d"), nota="Ajuste al editar (diferencia)")
                except Exception:
                    pass
            changed = True
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(reader)
    return changed

def registros_por_fecha(date_str):
    out = []
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return out
    for r in leer_registros():
        fi = (r.get("FechaIngreso") or "")[:19]
        fs = (r.get("FechaSalida") or "")[:19]
        try:
            fi_dt = _parse_dt_try(fi)
            fs_dt = _parse_dt_try(fs)
            if not fi_dt:
                continue
            if not fs_dt:
                noches = int(float(r.get("Noches") or 0))
                fs_dt = fi_dt + timedelta(days=noches)
        except:
            continue
        if fi_dt.date() <= d <= fs_dt.date():
            out.append(r)
    return out

def expandir_registro_a_dias(r):
    out = []
    fi_str = (r.get("FechaIngreso") or "")[:19]
    fs_str = (r.get("FechaSalida") or "")[:19]
    fi_dt = _parse_dt_try(fi_str)
    fs_dt = _parse_dt_try(fs_str)
    if not fi_dt:
        try:
            fi_dt = datetime.strptime((r.get("FechaIngreso") or "")[:10], "%Y-%m-%d")
        except:
            fi_dt = datetime.now()
    if not fs_dt:
        try:
            noches = int(float(r.get("Noches") or 0))
        except:
            noches = 1
        fs_dt = fi_dt + timedelta(days=noches)

    days = (fs_dt.date() - fi_dt.date()).days
    for i in range(days + 1):
        d = fi_dt.date() + timedelta(days=i)
        hora = fi_dt.strftime("%H:%M") if fi_dt else ""
        vr = {
            "ID": f"{r.get('ID')}-{i}",
            "Tipo": "PERRO",
            "Nombre": r.get("Nombre"),
            "Fecha": d.strftime("%Y-%m-%d"),
            "Hora": hora,
            "NochesPrevistas": "1",
            "Confirmado": r.get("Confirmado", "-") or "-",
            "Notas": r.get("Extras", "")
        }
        out.append(vr)
    return out

def cantidad_en_fecha(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return 0
    cnt = 0
    for r in leer_registros():
        fi = (r.get("FechaIngreso") or "")[:19]
        fs = (r.get("FechaSalida") or "")[:19]
        fi_dt = _parse_dt_try(fi)
        fs_dt = _parse_dt_try(fs)
        if not fi_dt:
            continue
        if not fs_dt:
            try:
                noches = int(float(r.get("Noches") or 0))
            except:
                noches = 1
            fs_dt = fi_dt + timedelta(days=noches)
        if fi_dt.date() <= d <= fs_dt.date():
            cnt += 1
    return cnt

def marcar_estado(rec_id, estado):
    p = ruta_registros()
    changed = False
    with open(p, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r.get("ID") == rec_id:
            r["EstadoPago"] = estado
            changed = True
    if changed:
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)
    return changed

def cancelar_registro(rec_id):
    # marca como cancelado pero conserva anticipo
    return marcar_estado(rec_id, "Cancelado")
