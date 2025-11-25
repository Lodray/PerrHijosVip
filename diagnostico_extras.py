# diagnostico_extras.py
import csv
from modules.utils import ruta_registros, carpeta_data
from modules import extras as extras_mod

def leer_csv(path):
    rows=[]
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print("No se pudo leer", path, e)
    return rows

extras = extras_mod.leer_todos()
regs = {}
for r in leer_csv(ruta_registros()):
    regs[r.get("ID")] = r

print("Extras encontrados:", len(extras))
for e in extras:
    monto = e.get("Monto") or e.get("monto") or ""
    rid = (e.get("RegistroID") or e.get("registro_id") or "").strip()
    exists = "SI" if rid and rid in regs else "NO" if rid else "SIN_REGID"
    print(f"Extra ID:{e.get('ID')} Monto:{monto} RegistroID:{rid or '(vacío)'} ExisteRegistro:{exists}")
    if exists == "SI":
        reg = regs[rid]
        print("   -> Registro Nombre:", reg.get("Nombre"), "EstadoPago:", reg.get("EstadoPago"), "Total:", reg.get("Total"))
