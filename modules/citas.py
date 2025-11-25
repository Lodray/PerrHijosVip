
# modules/citas.py
import os
import csv
from datetime import datetime
from modules.utils import ruta_citas, generar_id

HEADERS = ["ID","Tipo","Nombre","Fecha","Hora","NochesPrevistas","Telefono","Confirmado","Notas","FechaRegistro"]
# Tipo: "PERRO" o "PERSONA"

def asegurar_csv():
    p = ruta_citas()
    carpeta = os.path.dirname(p)
    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta, exist_ok=True)
    if not os.path.exists(p):
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def leer_citas():
    asegurar_csv()
    p = ruta_citas()
    rows = []
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def existe_cita(nombre, fecha_str, hora_str):
    for c in leer_citas():
        if (c.get("Nombre","").strip().lower() == (nombre or "").strip().lower() and
            (c.get("Fecha") or "") == (fecha_str or "") and
            (c.get("Hora") or "") == (hora_str or "")):
            return True
    return False

def agregar_cita_perro(nombre, fecha_str, hora_str, noches:int, anticipo, confirmado=False, notas=""):
    asegurar_csv()
    if existe_cita(nombre, fecha_str, hora_str):
        return None
    p = ruta_citas()
    nid = generar_id()
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(p, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nid, "PERRO", nombre, fecha_str, hora_str, str(noches), "", "Si" if confirmado else "No", notas, fecha_registro])
    return nid

def agregar_cita_persona(nombre, fecha_str, hora_str, telefono, confirmado=False, notas=""):
    asegurar_csv()
    if existe_cita(nombre, fecha_str, hora_str):
        return None
    p = ruta_citas()
    nid = generar_id()
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(p, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nid, "PERSONA", nombre, fecha_str, hora_str, "0", telefono, "Si" if confirmado else "No", notas, fecha_registro])
    return nid

def buscar_citas_por_nombre(term):
    term = (term or "").strip().lower()
    if not term:
        return leer_citas()
    return [c for c in leer_citas() if term in (c.get("Nombre") or "").lower()]

def citas_por_fecha(date_str):
    """Devuelve todas las citas registradas para una fecha dada (coincidencia por Fecha)."""
    res = []
    for c in leer_citas():
        if (c.get("Fecha") or "").startswith(date_str):
            res.append(c)
    return res

def confirmar_cita(cita_id):
    p = ruta_citas()
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    for r in reader:
        if r.get("ID") == cita_id:
            r["Confirmado"] = "Si"
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(reader)
    return True

def cancelar_cita(cita_id):
    """
    Marca la cita como cancelada sin borrarla. Se usa para conservar el anticipo en reportes.
    Simplemente actualiza el campo 'Confirmado' a 'Cancelada'.
    """
    p = ruta_citas()
    changed = False
    with open(p, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r.get("ID") == cita_id:
            r["Confirmado"] = "Cancelada"
            changed = True
    if changed:
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)
    return changed

def eliminar_cita(cita_id):
    p = ruta_citas()
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    nuevas = [r for r in reader if r.get("ID") != cita_id]
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(nuevas)
    return True

def actualizar_cita(cita_id, datos_dict):
    """
    Actualiza campos de una cita existente.
    datos_dict puede contener claves entre HEADERS (excepto ID).
    """
    p = ruta_citas()
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    changed = False
    for r in reader:
        if r.get("ID") == cita_id:
            for k, v in datos_dict.items():
                if k in r and k != "ID":
                    r[k] = v
            changed = True
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(reader)
    return changed

# ===== End of updated modules/citas.py =====
