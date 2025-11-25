# === FILE: modules/extras.py ===
import os
import csv
from datetime import datetime
from modules.utils import carpeta_data, generar_id

def ruta_extras():
    carpeta = carpeta_data()
    return os.path.join(carpeta, "extras.csv")

HEADERS = ["ID","RegistroID","Fecha","Monto","Nota","FechaRegistro"]

def asegurar_csv():
    p = ruta_extras()
    carpeta = os.path.dirname(p)
    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta, exist_ok=True)
    if not os.path.exists(p):
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def leer_todos():
    asegurar_csv()
    p = ruta_extras()
    rows = []
    if not os.path.exists(p):
        return rows
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def agregar_extra(registro_id, monto, fecha=None, nota=""):
    asegurar_csv()
    try:
        monto_f = float(monto)
    except:
        raise ValueError("Monto inválido")
    nid = generar_id()
    if fecha:
        try:
            if len(fecha) == 10:
                fecha_str = f"{fecha} 00:00:00"
            else:
                fecha_str = fecha[:19]
            datetime.strptime(fecha_str[:19], "%Y-%m-%d %H:%M:%S")
        except:
            fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_reg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p = ruta_extras()
    with open(p, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nid, str(registro_id).strip(), fecha_str, f"{monto_f:.2f}", nota or "", fecha_reg])
    return nid

def extras_por_fecha(date_str):
    out = []
    for e in leer_todos():
        if (e.get("Fecha") or "")[:10] == date_str:
            out.append(e)
    return out

def extras_en_rango(start_date, end_date):
    out = []
    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except:
        return out
    for e in leer_todos():
        try:
            d = datetime.strptime((e.get("Fecha") or "")[:10], "%Y-%m-%d").date()
            if sd <= d <= ed:
                out.append(e)
        except:
            continue
    return out

def extras_por_registro(registro_id):
    return [e for e in leer_todos() if (e.get("RegistroID") or "").strip() == (registro_id or "").strip()]

def eliminar_extras_por_registro(registro_id):
    """Elimina todas las filas de extras asociadas a registro_id y devuelve True si eliminó al menos una."""
    asegurar_csv()
    p = ruta_extras()
    changed = False
    with open(p, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    nuevas = [r for r in rows if (r.get("RegistroID") or "").strip() != (registro_id or "").strip()]
    if len(nuevas) != len(rows):
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(nuevas)
        changed = True
    return changed
