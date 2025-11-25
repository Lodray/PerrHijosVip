# diagnostico_extras_debug.py
import csv
import os
from datetime import datetime, timedelta
from modules import extras as extras_mod
from modules.utils import ruta_registros
try:
    from modules.reportes import _parse_date_try_local
except Exception:
    _parse_date_try_local = None

# Falla seguro si import circular; definimos localmente la función de parseo/reatribucion
def _parse_dt_local(s):
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

def leer_registros():
    p = ruta_registros()
    rows = []
    if not os.path.exists(p):
        return rows
    with open(p, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

# Ajusta estas fechas al mes/rango que estés reportando
# Por ejemplo: para noviembre 2025:
start_date = "2025-11-01"
end_date = "2025-11-30"
sd = datetime.strptime(start_date, "%Y-%m-%d").date()
ed = datetime.strptime(end_date, "%Y-%m-%d").date()

print("RANGO DIAGNÓSTICO:", start_date, "->", end_date)
extras = extras_mod.leer_todos()
regs = { r.get("ID"): r for r in leer_registros() }

print(f"Extras totales en archivo: {len(extras)}")
for e in extras:
    eid = e.get("ID")
    regid = (e.get("RegistroID") or "").strip()
    fecha_raw = (e.get("Fecha") or "")[:19]
    monto = e.get("Monto") or e.get("monto") or ""
    nota = e.get("Nota") or e.get("nota") or ""
    # parse fecha
    try:
        f_dt = datetime.strptime(fecha_raw[:10], "%Y-%m-%d").date()
    except Exception:
        f_dt = None
    reason = []
    included = False
    if not f_dt:
        reason.append("Fecha inválida -> excluir")
    else:
        # si tiene registro asociado
        if regid:
            reg = regs.get(regid)
            if not reg:
                reason.append(f"RegistroID {regid} NO existe -> extra huérfano -> excluir")
            else:
                # obtener FechaIngreso/Salida del registro
                fi = _parse_dt_local((reg.get("FechaIngreso") or "")[:19])
                fs = _parse_dt_local((reg.get("FechaSalida") or "")[:19])
                # si no hay fs, intentar calcular con noches
                if not fs and fi:
                    try:
                        noches = int(float(reg.get("Noches") or 0))
                    except:
                        noches = 0
                    fs = fi + timedelta(days=noches)
                # aplicar regla último día del mes
                atrib_date = f_dt
                if fi and fs:
                    year = f_dt.year; month = f_dt.month; day = f_dt.day
                    import calendar
                    last_day = calendar.monthrange(year, month)[1]
                    if day == last_day and fs.date() > f_dt:
                        atrib_date = f_dt + timedelta(days=1)
                        reason.append(f"Reatribución aplicada: {f_dt} -> {atrib_date}")
                # ahora decidir inclusión según EstadoPago del registro
                estado = (reg.get("EstadoPago") or "").strip().lower()
                if not (sd <= atrib_date <= ed):
                    reason.append(f"Atrib_date {atrib_date} fuera de rango")
                else:
                    if estado == "pagado":
                        included = True
                        reason.append("Registro pagado -> extra incluido en EXTRAS")
                    elif estado in ("anticipo","cancelado"):
                        included = True
                        reason.append("Registro anticipo/cancelado -> extra sumado al ANTICIPO")
                    else:
                        reason.append(f"Registro estado='{reg.get('EstadoPago')}' -> extra NO incluido por reglas")
        else:
            # extra independiente -> incluir si fecha en rango
            if f_dt and sd <= f_dt <= ed:
                included = True
                reason.append("Extra independiente (sin RegistroID) -> incluido")
            else:
                reason.append("Extra independiente fuera de rango -> excluir")

    print("-------------------------------------------------")
    print(f"Extra ID: {eid}")
    print(f"  RegistroID: '{regid or '(vacío)'}'")
    print(f"  Fecha (raw): {fecha_raw}  Fecha parsed: {f_dt}")
    print(f"  Monto: {monto}  Nota: {nota}")
    print("  Resultado: ", "INCLUIDO" if included else "EXCLUIDO")
    for r in reason:
        print("   -", r)
    # Si incluido además muestro estado del registro si lo hay
    if regid and regid in regs:
        reg = regs[regid]
        print("  -> Registro existe. Nombre:", reg.get("Nombre"), "EstadoPago:", reg.get("EstadoPago"), "Total:", reg.get("Total"))
print("DIAGNÓSTICO COMPLETO")
