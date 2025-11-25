# prueba_generar_reporte.py
import traceback
from modules import reportes

start_date = "2025-11-01"   # ajusta si necesitas otro mes
end_date = "2025-11-30"

try:
    res = reportes.generar_reporte_range(start_date, end_date, salida_excel=False, salida_pdf=False)
    print("REPORTE (obj):")
    print(res)
except Exception as e:
    print("OCURRIÓ UNA EXCEPCIÓN al generar reporte:")
    traceback.print_exc()
