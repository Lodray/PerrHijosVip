# modules/utils.py
import os
import uuid
import tempfile
import logging
import shutil
from datetime import datetime
import platform
import subprocess
import webbrowser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def carpeta_data():
    try:
        perfil = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        documentos = os.path.join(perfil, "Documents")
    except Exception:
        documentos = os.path.expanduser("~")
    carpeta = os.path.join(documentos, "PerrHijos", "data")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta

def ruta_config():
    return os.path.join(carpeta_data(), "config.json")

def ruta_registros():
    return os.path.join(carpeta_data(), "registros.csv")

def ruta_citas():
    return os.path.join(carpeta_data(), "citas.csv")

def ruta_reports_dir():
    d = os.path.join(carpeta_data(), "reports")
    os.makedirs(d, exist_ok=True)
    return d

def generar_id():
    return uuid.uuid4().hex

def atomic_write_text(path, text, encoding="utf-8"):
    dirn = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix="tmp_", dir=dirn, text=True)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass
        raise

def safe_replace_file_from_rows(path, fieldnames, rows, newline="", encoding="utf-8"):
    """
    Escribe CSV de forma atómica usando csv.DictWriter.
    rows: lista de dicts (se asume que las keys coinciden con fieldnames).
    """
    import csv, io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buf.getvalue(), encoding=encoding)

def abrir_archivo_ruta(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        try:
            webbrowser.open(path)
        except Exception:
            logger.exception("No se pudo abrir archivo: %s", path)

def parse_datetime_try(s):
    """Intenta parsear varios formatos y devuelve datetime o None"""
    if not s:
        return None
    s = s.strip()
    fmts = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d")
    for fmt in fmts:
        try:
            # tomar la porción necesaria
            return datetime.strptime(s[:len(fmt)], fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s)
    except Exception:
        logger.debug("parse_datetime_try falló para %r", s)
        return None

def format_datetime(dt):
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
