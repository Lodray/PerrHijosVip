# === FILE: modules/configuracion.py ===
import json, os
from modules.utils import ruta_config

DEFAULT = {
    "precio_por_noche": 250.0,
    "anticipo_porcentaje": 30.0,
    # nuevos ajustes para guarderia
    "precio_guarderia_por_hora": 50.0,
    "anticipo_guarderia_porcentaje": 30.0
}

def cargar_config():
    p = ruta_config()
    if not os.path.exists(p):
        guardar_config(DEFAULT)
        return DEFAULT.copy()
    try:
        with open(p, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k,v in DEFAULT.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except Exception:
        guardar_config(DEFAULT)
        return DEFAULT.copy()

def guardar_config(cfg):
    p = ruta_config()
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return True
