# crear_extras_header.py
from modules.extras import ruta_extras, asegurar_csv
p = ruta_extras()
print("Ruta donde se creará extras.csv ->", p)
asegurar_csv()
print("He ejecutado asegurar_csv(). Comprueba que el archivo existe ahora.")
try:
    with open(p, "r", encoding="utf-8") as f:
        print("Contenido inicial de extras.csv:")
        print(f.read()[:1000])
except Exception as e:
    print("Error al abrir extras.csv:", e)
