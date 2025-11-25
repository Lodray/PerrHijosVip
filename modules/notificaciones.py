# modules/notificaciones.py
from datetime import datetime, timedelta
from modules import citas, registro

def eventos_para_fecha(date_str):
    res=[]
    for c in citas.citas_por_fecha(date_str):
        if (c.get("Tipo") or "").upper() != "PERRO":
            res.append({"tipo":"CITA","subtipo":c.get("Tipo"), "nombre":c.get("Nombre"), "hora":c.get("Hora"), "id":c.get("ID")})
    # llegadas (FechaIngreso == date_str)
    for r in registro.leer_registros():
        fi = (r.get("FechaIngreso") or "")[:10]
        if fi == date_str:
            res.append({"tipo":"REGISTRO","nombre":r.get("Nombre"), "hora": (r.get("FechaIngreso") or "")[11:16], "id": r.get("ID")})
    return res

def eventos_para_manana():
    manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return eventos_para_fecha(manana)

def obtener_recordatorios_para_manana():
    return eventos_para_manana()
