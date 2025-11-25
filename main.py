# main.py
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

from modules import utils, configuracion, registro, citas, reportes, notificaciones, extras as extras_mod

# tkcalendar & PIL checks
try:
    from tkcalendar import Calendar, DateEntry
    TKCAL = True
except Exception:
    TKCAL = False

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

cfg = configuracion.cargar_config()

# build HORAS list (00/30)
HORAS = []
for h in range(8, 21):
    HORAS.append(f"{h:02d}:00")
    HORAS.append(f"{h:02d}:30")

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_NORMAL = ("Segoe UI", 10)
PALE_YELLOW = "#fff9db"
TABLE_BG = "#ffffff"
TEXT_COLOR = "#2f2f2f"
BTN_BLUE = "#1e3d59"
BTN_GREEN = "#2e7d32"
BTN_RED = "#c62828"
BTN_ORANGE = "#ff9800"
TAG_PAID = "pagado"
TAG_ANT = "anticipo"
TAG_NONE = "sinpago"
TAG_CANCEL = "cancelado"

def resource_path(*paths):
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, *paths)

root = tk.Tk()
root.title("PerrHijos VIP")
# make initial size adaptive to screen (keeps minimums reasonable)
sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
init_w = min(1200, max(1000, int(sw * 0.75)))
init_h = min(820, max(700, int(sh * 0.75)))
root.geometry(f"{init_w}x{init_h}")
root.minsize(900, 620)
root.configure(bg=PALE_YELLOW)

style = ttk.Style()
try:
    style.theme_use("clam")
except:
    pass
style.configure("TButton", padding=6, font=FONT_NORMAL)
style.configure("Treeview", rowheight=24, font=FONT_NORMAL)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

header = tk.Frame(root, bg=PALE_YELLOW); header.pack(side="top", fill="x")
tk.Label(header, text="PerrHijos VIP", font=("Segoe UI", 18, "bold"), bg=PALE_YELLOW, fg=TEXT_COLOR).pack(side="left", padx=12, pady=8)

logo_path = resource_path("assets", "logo.png")
if PIL_OK and os.path.exists(logo_path):
    try:
        img = Image.open(logo_path)
        img = img.resize((100, 72), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=photo, bg=PALE_YELLOW)
        lbl_logo.image = photo
        lbl_logo.pack(side="right", padx=12, pady=4)
    except Exception:
        pass

sidebar = tk.Frame(root, bg="#fffef6", width=240); sidebar.pack(side="left", fill="y", padx=(8, 6), pady=8)
content_area = tk.Frame(root, bg=PALE_YELLOW); content_area.pack(side="right", fill="both", expand=True, padx=(6,12), pady=8)
content_area.current_table = None

# ---------------- CORRECCIÓN: función limpiar necesaria ----------------
def limpiar(frame):
    """
    Limpia el contenido de un frame (elimina widgets hijos) y resetea current_table.
    Debe estar definida antes de usar panel_registro / panel_citas / etc.
    """
    try:
        for w in frame.winfo_children():
            w.destroy()
        try:
            frame.current_table = None
        except Exception:
            pass
    except Exception:
        pass

def fmt_human_date_time(date_str_iso, time_str_hhmm=""):
    try:
        if not date_str_iso: return ""
        d = datetime.strptime(date_str_iso, "%Y-%m-%d")
        date_part = d.strftime("%d/%m/%Y")
        if time_str_hhmm:
            try:
                t = datetime.strptime(time_str_hhmm, "%H:%M")
                time_part = t.strftime("%-I:%M %p") if sys.platform != "win32" else t.strftime("%#I:%M %p")
                return f"{date_part} – {time_part}"
            except:
                return date_part
        return date_part
    except:
        return date_str_iso

# ---------------- PANEL REGISTRO ----------------
def panel_registro(parent):
    limpiar(parent)
    panel = tk.Frame(parent, bg=TABLE_BG, padx=8, pady=8); panel.pack(fill="both", expand=True)
    tk.Label(panel, text="Registro de estancias / guardería", font=FONT_TITLE, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0,6))

    form = tk.Frame(panel, bg=TABLE_BG); form.pack(fill="x", padx=6, pady=(6,6))
    # Nombre
    tk.Label(form, text="Nombre (Cliente o mascota):", font=FONT_LABEL, bg=TABLE_BG).grid(row=0,column=0,sticky="w")
    e_nombre = tk.Entry(form, font=FONT_NORMAL, width=28); e_nombre.grid(row=1,column=0,sticky="w", padx=(0,6))
    # Cantidad de mascotas
    tk.Label(form, text="Cantidad (perros):", font=FONT_LABEL, bg=TABLE_BG).grid(row=0,column=1,sticky="w", padx=(8,0))
    e_cantidad = tk.Entry(form, font=FONT_NORMAL, width=6); e_cantidad.insert(0,"1"); e_cantidad.grid(row=1,column=1,sticky="w", padx=(8,6))
    # Noches
    tk.Label(form, text="Noches:", font=FONT_LABEL, bg=TABLE_BG).grid(row=0,column=2,sticky="w", padx=(8,0))
    e_noches = tk.Entry(form, font=FONT_NORMAL, width=8); e_noches.insert(0,"1"); e_noches.grid(row=1,column=2,sticky="w", padx=(8,6))
    # Extras
    tk.Label(form, text="Extras (MXN):", font=FONT_LABEL, bg=TABLE_BG).grid(row=2,column=0,sticky="w", pady=(8,0))
    e_extras = tk.Entry(form, font=FONT_NORMAL, width=14); e_extras.insert(0,"0"); e_extras.grid(row=3,column=0,sticky="w", padx=(0,6))
    # Fecha ingreso
    tk.Label(form, text="Fecha ingreso:", font=FONT_LABEL, bg=TABLE_BG).grid(row=2,column=1,sticky="w", padx=(8,0))
    e_fecha = tk.Entry(form, font=FONT_NORMAL, width=12); e_fecha.grid(row=3,column=1,sticky="w", padx=(8,6))
    # Hora entrada
    tk.Label(form, text="Hora entrada:", font=FONT_LABEL, bg=TABLE_BG).grid(row=2,column=2,sticky="w", padx=(8,0))
    e_hora = ttk.Combobox(form, values=HORAS, state="readonly", width=10); e_hora.set(HORAS[0]); e_hora.grid(row=3,column=2,sticky="w", padx=(8,6))

    # botones
    btn_reg = tk.Button(form, text="Registrar estancia", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, width=16); btn_reg.grid(row=1,column=3,rowspan=2,padx=(16,0),sticky="n")
    btn_guard = tk.Button(form, text="Registrar guardería", bg=BTN_ORANGE, fg="white", font=FONT_NORMAL, width=16); btn_guard.grid(row=3,column=3,rowspan=1,padx=(16,0),sticky="n")

    body = tk.Frame(panel, bg=TABLE_BG); body.pack(fill="both", expand=True, pady=(8,0))
    # make both sides responsive
    left = tk.Frame(body, bg=TABLE_BG); left.pack(side="left", fill="both", expand=True, padx=(6,8), pady=2)
    right = tk.Frame(body, bg=TABLE_BG); right.pack(side="right", fill="both", expand=True, padx=(8,6))

    if TKCAL:
        cal = Calendar(left, selectmode="day", date_pattern="yyyy-mm-dd", font=FONT_NORMAL, showweeknumbers=False)
        cal.pack(fill="both", expand=True, padx=6, pady=6)
    else:
        tk.Label(left, text="Instala tkcalendar para calendario interactivo", bg=TABLE_BG).pack(padx=12, pady=12)
        cal = None

    # ACTIONS: top row (Eliminar, Modificar, Buscar, Mostrar) arranged right->left visually
    actions = tk.Frame(right, bg=TABLE_BG); actions.pack(fill="x", padx=6, pady=(6,4))
    # we'll pack side='right' in order: Mostrar, Buscar, Editar, Eliminar -> left->right will be Eliminar,...,Mostrar
    btn_show = tk.Button(actions, text="Mostrar todos", bg="#198754", fg="white", font=FONT_NORMAL, width=12)
    btn_search = tk.Button(actions, text="Buscar", bg="#1976d2", fg="white", font=FONT_NORMAL, width=10)
    e_search = tk.Entry(actions, font=FONT_NORMAL, width=20)
    btn_edit = tk.Button(actions, text="Modificar registro", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, width=16)
    btn_delete = tk.Button(actions, text="Eliminar registro", bg=BTN_RED, fg="white", font=FONT_NORMAL, width=14)
    # pack in this order so visual right->left is: Eliminar, Modificar, Buscar, Mostrar
    btn_show.pack(side="right", padx=(6,0))
    btn_search.pack(side="right", padx=(6,0))
    e_search.pack(side="right", padx=(6,0))
    btn_edit.pack(side="right", padx=(6,0))
    btn_delete.pack(side="right", padx=(6,0))

    # Second row: payment/cancel buttons (right->left: Cancelar, Pagado completo, Solo anticipo, Sin pago)
    pay_frame = tk.Frame(right, bg=TABLE_BG); pay_frame.pack(fill="x", padx=6, pady=(6,4))
    btn_pay_none = tk.Button(pay_frame, text="Marcar sin pago", bg="#eeeeee", fg="black", font=FONT_NORMAL, width=16)
    btn_pay_antic = tk.Button(pay_frame, text="Marcar solo anticipo", bg="#f4c542", fg="black", font=FONT_NORMAL, width=18)
    btn_pay_all = tk.Button(pay_frame, text="Marcar pagado completo", bg=BTN_GREEN, fg="white", font=FONT_NORMAL, width=18)
    btn_cancel = tk.Button(pay_frame, text="Cancelar reserva", bg="#6c757d", fg="white", font=FONT_NORMAL, width=16)
    # pack in order so visual right->left: Cancelar, Pagado, Anticipo, Sin pago
    btn_pay_none.pack(side="right", padx=(6,0))
    btn_pay_antic.pack(side="right", padx=(6,0))
    btn_pay_all.pack(side="right", padx=(6,0))
    btn_cancel.pack(side="right", padx=(6,0))

    # tabla
    cols = ("Nombre","Cantidad","Noches","Extras","Total","Anticipo","Restante","Fecha-Ingreso","Fecha-Salida","Servicio","Estado-Pago")
    tbl = ttk.Treeview(right, columns=cols, show="headings", height=16)
    widths = [160,60,60,70,80,80,80,140,140,100,100]
    for c,w in zip(cols,widths):
        tbl.heading(c, text=c); tbl.column(c, width=w, anchor="center", stretch=True)
    vsb = ttk.Scrollbar(right, orient="vertical", command=tbl.yview); tbl.configure(yscroll=vsb.set); vsb.pack(side="right", fill="y")
    hsb = ttk.Scrollbar(right, orient="horizontal", command=tbl.xview); tbl.configure(xscroll=hsb.set); hsb.pack(side="bottom", fill="x")
    tbl.pack(fill="both", expand=True, pady=(6,0))
    parent.current_table = tbl

    # tag colors
    try:
        tbl.tag_configure(TAG_PAID, background="#d7f2d8")
        tbl.tag_configure(TAG_ANT, background="#fff4c2")
        tbl.tag_configure(TAG_NONE, background="#ffffff")
        tbl.tag_configure(TAG_CANCEL, background="#dcdcdc")
    except Exception:
        pass

    def llenar_tabla_reg(rows):
        for it in tbl.get_children(): tbl.delete(it)
        for r in rows:
            iid = r.get("ID")
            tag = TAG_NONE
            estado = (r.get("EstadoPago") or "").lower()
            if estado == "pagado":
                tag = TAG_PAID
            elif estado == "anticipo":
                tag = TAG_ANT
            elif estado == "cancelado":
                tag = TAG_CANCEL
            tbl.insert("", "end", iid=iid, values=(
                r.get("Nombre"), r.get("Cantidad") or "1", r.get("Noches"), r.get("Extras"),
                r.get("Total"), r.get("Anticipo"), r.get("Restante"),
                (r.get("FechaIngreso") or "")[:16], (r.get("FechaSalida") or "")[:16], r.get("Servicio","Estancia"), r.get("EstadoPago","")
            ), tags=(tag,))

    def actualizar_tabla_reg(selected_date=None):
        if selected_date:
            rows = registro.registros_por_fecha(selected_date)
        else:
            rows = registro.leer_registros()
        llenar_tabla_reg(rows)

    def buscar_action(event=None):
        term = e_search.get().strip()
        if not term:
            actualizar_tabla_reg()
            return
        datos = registro.buscar_registros_por_nombre(term)
        llenar_tabla_reg(datos)

    def editar_sel():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Editar","Selecciona un registro.")
            return
        rec_id = sel[0]
        rec = next((x for x in registro.leer_registros() if x.get("ID")==rec_id), None)
        if not rec:
            messagebox.showerror("Editar","Registro no encontrado.")
            return
        win = tk.Toplevel(root); win.title("Editar registro"); win.geometry("520x340"); win.configure(bg=PALE_YELLOW)
        tk.Label(win, text="Editar registro", font=FONT_LABEL, bg=PALE_YELLOW).pack(pady=6)
        f = tk.Frame(win, bg=PALE_YELLOW); f.pack(padx=12, pady=8, fill="x")
        tk.Label(f, text="Nombre:", bg=PALE_YELLOW).grid(row=0,column=0,sticky="w")
        en = tk.Entry(f); en.insert(0, rec.get("Nombre")); en.grid(row=0,column=1,sticky="w")
        tk.Label(f, text="Cantidad:", bg=PALE_YELLOW).grid(row=1,column=0,sticky="w")
        ec = tk.Entry(f); ec.insert(0, rec.get("Cantidad") or "1"); ec.grid(row=1,column=1,sticky="w")
        tk.Label(f, text="Noches:", bg=PALE_YELLOW).grid(row=2,column=0,sticky="w")
        eno = tk.Entry(f); eno.insert(0, rec.get("Noches") or "0"); eno.grid(row=2,column=1,sticky="w")
        tk.Label(f, text="Extras (MXN):", bg=PALE_YELLOW).grid(row=3,column=0,sticky="w")
        ex = tk.Entry(f); ex.insert(0, rec.get("Extras") or "0"); ex.grid(row=3,column=1,sticky="w")
        tk.Label(f, text="Fecha (YYYY-MM-DD):", bg=PALE_YELLOW).grid(row=4,column=0,sticky="w")
        if TKCAL:
            edate = DateEntry(f, date_pattern="yyyy-mm-dd", width=12)
            try:
                edate.set_date((rec.get("FechaIngreso") or "")[:10])
            except:
                pass
        else:
            edate = tk.Entry(f); edate.insert(0,(rec.get("FechaIngreso") or "")[:10])
        edate.grid(row=4,column=1,sticky="w")
        tk.Label(f, text="Hora:", bg=PALE_YELLOW).grid(row=5,column=0,sticky="w")
        eh = ttk.Combobox(f, values=HORAS, state="readonly", width=10); eh.set((rec.get("FechaIngreso") or "")[11:16] or HORAS[0]); eh.grid(row=5,column=1,sticky="w")
        tk.Label(f, text="Servicio:", bg=PALE_YELLOW).grid(row=6,column=0,sticky="w")
        serv_cb = ttk.Combobox(f, values=["Estancia","Guarderia"], state="readonly", width=12); serv_cb.set(rec.get("Servicio","Estancia")); serv_cb.grid(row=6,column=1,sticky="w")
        tk.Label(f, text="Dur (min) (guardería):", bg=PALE_YELLOW).grid(row=7,column=0,sticky="w")
        edur = tk.Entry(f); edur.insert(0, rec.get("DurationMinutes","")); edur.grid(row=7,column=1,sticky="w")

        def guardar():
            try:
                nombre_n = en.get().strip()
                cantidad_n = int(ec.get().strip() or 1)
                noches_i = int(float(eno.get().strip() or 0))
                extras_f = float(ex.get().strip() or 0.0)
                fecha_s = edate.get().strip() if hasattr(edate, "get") else edate.get()
                hora_s = eh.get().strip()
                servicio_n = serv_cb.get().strip()
                # duration stored in minutes in CSV/module
                try:
                    durmins = int(edur.get().strip() or 0)
                except:
                    durmins = 0
            except Exception:
                messagebox.showerror("Error","Valores inválidos."); return
            try:
                # intentar llamar a la función actualizar_registro con campos extendidos (cantidad, servicio, duration_minutes)
                try:
                    registro.actualizar_registro(rec_id, nombre_n, noches_i, extras_f, cfg.get("precio_por_noche",250.0),
                                                 cfg.get("anticipo_porcentaje",30.0), fecha_ingreso=f"{fecha_s} {hora_s}:00",
                                                 cantidad=cantidad_n, servicio=servicio_n, duration_minutes=durmins)
                except TypeError:
                    # versión antigua del módulo registro: llamar con firma clásica
                    registro.actualizar_registro(rec_id, nombre_n, noches_i, extras_f, cfg.get("precio_por_noche",250.0),
                                                 cfg.get("anticipo_porcentaje",30.0), fecha_ingreso=f"{fecha_s} {hora_s}:00")
                # refrescar la vista y mantener consistencia entre tabla y reportes
                messagebox.showinfo("Guardado","Registro actualizado.")
                win.destroy()
                # si se usa calendario, refrescar según fecha seleccionada, si no, refrescar todo
                try:
                    sel_date = cal.get_date() if (TKCAL and 'cal' in locals() and cal is not None) else None
                except Exception:
                    sel_date = None
                if TKCAL and sel_date:
                    actualizar_tabla_reg(sel_date)
                else:
                    actualizar_tabla_reg()
            except Exception as e:
                messagebox.showerror("Error","No se pudo guardar: "+str(e))

        tk.Button(win, text="Guardar", bg=BTN_BLUE, fg="white", command=guardar).pack(pady=10)

    def eliminar_sel():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Eliminar","Selecciona un registro.")
            return
        if not messagebox.askyesno("Confirmar","¿Eliminar registro? Esta acción borra también los extras asociados."):
            return
        registro.eliminar_por_id(sel[0])
        extras_mod.eliminar_extras_por_registro(sel[0])
        messagebox.showinfo("Eliminado","Registro eliminado.")
        if TKCAL and cal is not None:
            actualizar_tabla_reg(cal.get_date())
        else:
            actualizar_tabla_reg()

    def cancelar_sel():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Cancelar","Selecciona un registro.")
            return
        if not messagebox.askyesno("Confirmar","¿Deseas cancelar la reserva? (El anticipo se conservará)"):
            return
        registro.cancelar_registro(sel[0])
        messagebox.showinfo("Cancelado","Reserva marcada como cancelada. El anticipo se conserva.")
        if TKCAL and cal is not None:
            actualizar_tabla_reg(cal.get_date())
        else:
            actualizar_tabla_reg()

    def marcar_pagado_total():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Estado pago","Selecciona un registro.")
            return
        registro.marcar_estado(sel[0], "Pagado")
        actualizar_tabla_reg(cal.get_date() if TKCAL and cal is not None else None)

    def marcar_pagado_anticipo():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Estado pago","Selecciona un registro.")
            return
        registro.marcar_estado(sel[0], "Anticipo")
        actualizar_tabla_reg(cal.get_date() if TKCAL and cal is not None else None)

    def marcar_sin_pago():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Estado pago","Selecciona un registro.")
            return
        registro.marcar_estado(sel[0], "")
        actualizar_tabla_reg(cal.get_date() if TKCAL and cal is not None else None)

    # vincular botones
    btn_search.config(command=buscar_action)
    btn_show.config(command=lambda: [e_search.delete(0,tk.END), actualizar_tabla_reg(None)])
    btn_edit.config(command=editar_sel)
    btn_delete.config(command=eliminar_sel)
    btn_cancel.config(command=cancelar_sel)
    btn_pay_all.config(command=marcar_pagado_total)
    btn_pay_antic.config(command=marcar_pagado_anticipo)
    btn_pay_none.config(command=marcar_sin_pago)

    # ENTER bindings
    e_nombre.bind("<Return>", lambda e: e_cantidad.focus_set() if 'e_cantidad' in locals() else e_noches.focus_set())
    e_noches.bind("<Return>", lambda e: e_extras.focus_set())
    e_extras.bind("<Return>", lambda e: e_fecha.focus_set())
    e_fecha.bind("<Return>", lambda e: e_hora.focus_set())
    e_search.bind("<Return>", buscar_action)
    e_search.bind("<KP_Enter>", buscar_action)

    # registrar estancia
    def registrar_callback(event=None):
        nombre = e_nombre.get().strip()
        noches_s = e_noches.get().strip()
        extras_s = e_extras.get().strip()
        fecha = e_fecha.get().strip()
        hora = e_hora.get().strip()
        cantidad_s = e_cantidad.get().strip() or "1"
        if not nombre:
            messagebox.showwarning("Validación","Nombre requerido."); return
        try:
            noches_i = int(float(noches_s))
        except:
            messagebox.showwarning("Validación","Noches inválidas."); return
        try:
            extras_f = float(extras_s) if extras_s.strip()!="" else 0.0
        except:
            messagebox.showwarning("Validación","Extras inválidos."); return
        try:
            cantidad_i = int(cantidad_s)
            if cantidad_i < 1: raise ValueError()
        except:
            messagebox.showwarning("Validación","Cantidad inválida."); return
        if not fecha:
            messagebox.showwarning("Validación","Selecciona una fecha en el calendario."); return
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except:
            messagebox.showwarning("Validación","Fecha inválida."); return
        if hora not in HORAS:
            messagebox.showwarning("Validación","Selecciona una hora válida."); return

        fecha_ingreso_str = f"{fecha} {hora}:00"
        # verificar capacidad por día (limite 15) - se considera cada mascota como 1
        fs_dt = registro.calcular_fecha_salida_dt(fecha_ingreso_str, noches_i)
        cur = datetime.strptime(fecha_ingreso_str, "%Y-%m-%d %H:%M:%S")
        conflict = False
        while cur < fs_dt:
            cnt = registro.cantidad_en_fecha(cur.strftime("%Y-%m-%d"))
            # contabilizamos por registro (si cliente trae N perros, contamos N)
            if cnt >= 15:
                conflict = True; break
            cur = cur + timedelta(days=1)
        if conflict:
            if not messagebox.askyesno("Capacidad", "No hay espacio en al menos uno de los días seleccionados. ¿Deseas registrar de todos modos?"):
                return

        nid = registro.agregar_registro(nombre, noches_i, cfg.get("precio_por_noche",250.0), extras_f, cfg.get("anticipo_porcentaje",30.0),
                                        fecha_ingreso=fecha_ingreso_str, cantidad=cantidad_i, servicio="Estancia")
        messagebox.showinfo("Registrado","Perro(s) registrado(s).")
        e_nombre.delete(0,tk.END); e_noches.delete(0,tk.END); e_noches.insert(0,"1")
        e_extras.delete(0,tk.END); e_extras.insert(0,"0")
        e_cantidad.delete(0,tk.END); e_cantidad.insert(0,"1")
        e_hora.set(HORAS[0])
        if TKCAL and cal is not None:
            actualizar_tabla_reg(cal.get_date()); mostrar_para_fecha(cal.get_date())
        else:
            actualizar_tabla_reg()

    btn_reg.config(command=registrar_callback)

    # modal register guarderia
    def registrar_guarderia_modal(prefill_date):
        win = tk.Toplevel(root); win.title("Registrar guardería"); win.geometry("420x320"); win.configure(bg=PALE_YELLOW)
        tk.Label(win, text="Registrar Guardería (precio por hora configurable)", font=FONT_LABEL, bg=PALE_YELLOW).pack(pady=8)
        f = tk.Frame(win, bg=PALE_YELLOW); f.pack(padx=12, pady=6, fill="x")
        tk.Label(f, text="Nombre:", bg=PALE_YELLOW).grid(row=0,column=0,sticky="w")
        en = tk.Entry(f); en.grid(row=0,column=1,sticky="w")
        tk.Label(f, text="Fecha:", bg=PALE_YELLOW).grid(row=1,column=0,sticky="w")
        if TKCAL:
            ed = DateEntry(f, date_pattern="yyyy-mm-dd", width=12)
            try: ed.set_date(prefill_date)
            except: pass
        else:
            ed = tk.Entry(f); ed.insert(0, prefill_date)
        ed.grid(row=1,column=1,sticky="w")
        tk.Label(f, text="Hora inicio:", bg=PALE_YELLOW).grid(row=2,column=0,sticky="w")
        start_cb = ttk.Combobox(f, values=HORAS, state="readonly", width=10); start_cb.set(HORAS[0]); start_cb.grid(row=2,column=1,sticky="w")
        tk.Label(f, text="Duración (horas):", bg=PALE_YELLOW).grid(row=3,column=0,sticky="w")
        # duration selector in integer hours, default 8
        dur_spin = tk.Spinbox(f, from_=1, to=24, increment=1, width=8)
        dur_spin.delete(0,tk.END); dur_spin.insert(0, "8")
        dur_spin.grid(row=3,column=1,sticky="w")
        tk.Label(f, text="Cantidad mascotas:", bg=PALE_YELLOW).grid(row=4,column=0,sticky="w")
        cnt = tk.Entry(f); cnt.insert(0,"1"); cnt.grid(row=4,column=1,sticky="w")

        def crear_guarderia():
            nombre = en.get().strip()
            fecha = ed.get().strip()
            hora = start_cb.get().strip()
            try:
                dur = int(dur_spin.get())
                cantidad_i = int(cnt.get().strip() or 1)
            except:
                messagebox.showwarning("Validación","Duración o cantidad inválida."); return
            if not nombre or not fecha:
                messagebox.showwarning("Validación","Nombre y fecha obligatorios."); return
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except:
                messagebox.showwarning("Validación","Fecha inválida."); return
            if hora not in HORAS:
                messagebox.showwarning("Validación","Selecciona hora válida."); return

            fecha_ingreso_str = f"{fecha} {hora}:00"
            # use guarderia price per hour from config
            precio_hora = cfg.get("precio_guarderia_por_hora", cfg.get("precio_por_noche",250.0))
            # agregar registro con servicio guarderia and duration_minutes
            nid = registro.agregar_registro(nombre, 0, precio_hora, 0.0, cfg.get("anticipo_guarderia_porcentaje", cfg.get("anticipo_porcentaje",30.0)),
                                            fecha_ingreso=fecha_ingreso_str, cantidad=cantidad_i, servicio="Guarderia", duration_minutes=dur*60)
            messagebox.showinfo("Guardería","Guardería registrada.")
            win.destroy()
            if TKCAL and cal is not None:
                actualizar_tabla_reg(cal.get_date()); mostrar_para_fecha(cal.get_date())
            else:
                actualizar_tabla_reg()

        tk.Button(win, text="Registrar guardería", bg=BTN_BLUE, fg="white", command=crear_guarderia).pack(pady=10)

    btn_guard.config(command=lambda: registrar_guarderia_modal(cal.get_date() if cal else datetime.now().strftime("%Y-%m-%d")))

    def mostrar_para_fecha(date_str):
        e_fecha.delete(0,tk.END); e_fecha.insert(0, date_str)
        actualizar_tabla_reg(date_str)

    def actualizar_events_reg():
        if not TKCAL or cal is None:
            return
        try:
            for ev in cal.get_calevents():
                cal.calevent_remove(ev)
        except:
            pass
        for r in registro.leer_registros():
            try:
                expanded = registro.expandir_registro_a_dias(r) if hasattr(registro, "expandir_registro_a_dias") else []
                if not expanded:
                    fi = r.get("FechaIngreso","")[:10]; fs = r.get("FechaSalida","")[:10]
                    try:
                        sdt = datetime.strptime(fi, "%Y-%m-%d"); edt = datetime.strptime(fs, "%Y-%m-%d")
                        cur = sdt
                        while cur <= edt:
                            cal.calevent_create(cur.strftime("%Y-%m-%d"), r.get("Nombre","")[:12], tags=("stay",), background="orange")
                            cur += timedelta(days=1)
                    except:
                        pass
                else:
                    for vr in expanded:
                        cal.calevent_create(vr.get("Fecha"), vr.get("Nombre"), tags=("stay",), background="orange")
            except:
                pass

    if TKCAL and cal is not None:
        cal.bind("<<CalendarSelected>>", lambda e: mostrar_para_fecha(cal.get_date()))
        actualizar_events_reg()
        hoy = datetime.now().strftime("%Y-%m-%d")
        try: cal.selection_set(hoy)
        except: pass
        mostrar_para_fecha(hoy)
    else:
        actualizar_tabla_reg()

# ---------------- RECORDATORIOS NOTIFICACIONES ---------------
def mostrar_recordatorios():
    items = notificaciones.eventos_para_manana()
    if not items:
        messagebox.showinfo("Recordatorios", "No hay eventos para mañana.")
        return

    dlg = tk.Toplevel(root)
    dlg.title("Recordatorios - Mañana")
    dlg.geometry("620x420")
    dlg.configure(bg=PALE_YELLOW)

    tk.Label(dlg, text="Eventos para mañana", font=FONT_TITLE, bg=PALE_YELLOW).pack(pady=8)

    frame = tk.Frame(dlg, bg=PALE_YELLOW)
    frame.pack(fill="both", expand=True, padx=10, pady=6)

    lb = tk.Listbox(frame, font=FONT_NORMAL, activestyle="none", height=12)
    lb.pack(side="left", fill="both", expand=True, padx=(0,6))
    vs = ttk.Scrollbar(frame, orient="vertical", command=lb.yview)
    vs.pack(side="left", fill="y")
    lb.config(yscrollcommand=vs.set)

    eventos = list(items)
    for it in eventos:
        tipo = (it.get("tipo") or it.get("Tipo") or "").upper()
        nombre = it.get("nombre") or it.get("Nombre") or "Sin nombre"
        hora = it.get("hora") or ""
        icon = "🐶" if tipo == "REGISTRO" else "👤"
        confirm_flag = ""
        if tipo == "CITA" and ((it.get("confirmado") or "").lower().startswith("s") or (it.get("Confirmado") or "").lower().startswith("s")):
            confirm_flag = " (Confirmada)"
        lb.insert("end", f"{icon} {nombre} — {hora}{confirm_flag}")

    # detalles (derecha)
    right = tk.Frame(dlg, bg=PALE_YELLOW)
    right.pack(side="right", fill="y", padx=8, pady=8)

    detalle_lbl = tk.Label(right, text="Selecciona un evento", font=FONT_LABEL, bg=PALE_YELLOW, justify="left", wraplength=260)
    detalle_lbl.pack(anchor="nw", pady=(6,12))

    btn_confirm = tk.Button(right, text="Confirmar cita", bg=BTN_GREEN, fg="white", font=FONT_NORMAL, state="disabled", width=18)
    btn_confirm.pack(pady=(4,6))
    btn_edit_reg = tk.Button(right, text="Editar registro", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, state="disabled", width=18)
    btn_edit_reg.pack(pady=(4,6))
    tk.Button(right, text="Cerrar", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=dlg.destroy).pack(side="bottom", pady=10)

    selected_index = {"i": None}

    def actualizar_lista_local():
        nonlocal eventos
        eventos = notificaciones.eventos_para_manana()
        lb.delete(0, "end")
        for it in eventos:
            tipo = (it.get("tipo") or it.get("Tipo") or "").upper()
            nombre = it.get("nombre") or it.get("Nombre") or "Sin nombre"
            hora = it.get("hora") or ""
            icon = "🐶" if tipo == "REGISTRO" else "👤"
            confirm_flag = ""
            if tipo == "CITA" and ((it.get("confirmado") or "").lower().startswith("s") or (it.get("Confirmado") or "").lower().startswith("s")):
                confirm_flag = " (Confirmada)"
            lb.insert("end", f"{icon} {nombre} — {hora}{confirm_flag}")
        detalle_lbl.config(text="Selecciona un evento")
        btn_confirm.config(state="disabled")
        btn_edit_reg.config(state="disabled")
        selected_index["i"] = None

    def on_select(evt):
        sel = lb.curselection()
        if not sel:
            return
        i = sel[0]; selected_index["i"] = i
        it = eventos[i]
        tipo = (it.get("tipo") or it.get("Tipo") or "").upper()
        nombre = it.get("nombre") or it.get("Nombre") or "Sin nombre"
        hora = it.get("hora") or ""
        # mostrar detalle sin ID para aspecto profesional
        txt = f"Tipo: {tipo}\nNombre: {nombre}\nHora: {hora}"
        detalle_lbl.config(text=txt)
        if tipo == "CITA":
            btn_confirm.config(state="normal")
            btn_edit_reg.config(state="disabled")
        else:
            btn_confirm.config(state="disabled")
            btn_edit_reg.config(state="normal")

    def confirmar_seleccion():
        i = selected_index["i"]
        if i is None:
            messagebox.showwarning("Confirmar","Selecciona primero un evento de tipo cita.")
            return
        it = eventos[i]
        cid = it.get("id") or it.get("ID")
        try:
            citas.confirmar_cita(cid)
            messagebox.showinfo("Confirmado","Cita marcada como confirmada.")
            actualizar_lista_local()
        except Exception as e:
            messagebox.showerror("Error","No se pudo confirmar la cita:\n"+str(e))

    def editar_registro_seleccion():
        i = selected_index["i"]
        if i is None:
            messagebox.showwarning("Editar","Selecciona primero un registro.")
            return
        it = eventos[i]
        rid = it.get("id") or it.get("ID")
        rec = next((r for r in registro.leer_registros() if r.get("ID")==rid), None)
        if not rec:
            messagebox.showerror("Error","Registro no encontrado.")
            return
        try:
            panel_registro(content_area)
            if content_area.current_table is not None:
                try:
                    content_area.current_table.selection_set(rid)
                except:
                    pass
        except Exception:
            messagebox.showwarning("Aviso","No se pudo abrir panel de registro.")

    lb.bind("<<ListboxSelect>>", on_select)
    btn_confirm.config(command=confirmar_seleccion)
    btn_edit_reg.config(command=editar_registro_seleccion)

# ---------------- PANEL CITAS (sin cambios mayores) ----------------
def panel_citas(parent):
    limpiar(parent)
    panel = tk.Frame(parent, bg=TABLE_BG, padx=10, pady=10); panel.pack(fill="both", expand=True)
    tk.Label(panel, text="Citas y calendario (solo visitas)", font=FONT_TITLE, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0,6))

    top_actions = tk.Frame(panel, bg=TABLE_BG); top_actions.pack(fill="x", pady=(4,8))
    actions_left = tk.Frame(top_actions, bg=TABLE_BG); actions_left.pack(side="left", anchor="w", padx=(6,6))
    btn_new = tk.Button(actions_left, text="Nueva Cita", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, width=12); btn_new.pack(side="left", padx=(0,6))
    btn_edit = tk.Button(actions_left, text="Editar", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, width=10); btn_edit.pack(side="left", padx=(0,6))
    btn_delete = tk.Button(actions_left, text="Eliminar", bg=BTN_RED, fg="white", font=FONT_NORMAL, width=10); btn_delete.pack(side="left", padx=(0,6))
    btn_confirm = tk.Button(actions_left, text="Confirmar", bg=BTN_GREEN, fg="white", font=FONT_NORMAL, width=10); btn_confirm.pack(side="left")

    actions_right = tk.Frame(top_actions, bg=TABLE_BG); actions_right.pack(side="right", anchor="e", padx=(6,6))
    e_bus = tk.Entry(actions_right, font=FONT_NORMAL, width=28); e_bus.pack(side="left", padx=(0,8))
    btn_bus = tk.Button(actions_right, text="Buscar", bg="#1976d2", fg="white", font=FONT_NORMAL, width=10); btn_bus.pack(side="left", padx=(0,6))
    btn_show_all = tk.Button(actions_right, text="Mostrar todos", bg="#198754", fg="white", font=FONT_NORMAL, width=12); btn_show_all.pack(side="left")

    body = tk.Frame(panel, bg=TABLE_BG); body.pack(fill="both", expand=True, pady=(4,0))
    left = tk.Frame(body, bg=TABLE_BG); left.pack(side="left", fill="both", expand=True, padx=(6,8))
    right = tk.Frame(body, bg=TABLE_BG, width=440); right.pack(side="right", fill="both", expand=False, padx=(8,6))

    if TKCAL:
        cal = Calendar(left, selectmode="day", date_pattern="yyyy-mm-dd", font=FONT_NORMAL); cal.pack(fill="both", expand=True, padx=6, pady=6)
    else:
        tk.Label(left, text="Instala tkcalendar para calendario interactivo", bg=TABLE_BG, fg=TEXT_COLOR).pack(padx=12, pady=12)
        cal = None

    # nueva cita modal (persona) - reutilizado del main original
    def nueva_cita_modal(prefill_date):
        import traceback
        win = tk.Toplevel(root)
        win.title("Crear nueva cita (persona)")
        win.geometry("480x300")
        win.configure(bg=PALE_YELLOW)

        tk.Label(win, text="Crear nueva cita — Persona", font=FONT_TITLE, bg=PALE_YELLOW).pack(pady=8)
        f = tk.Frame(win, bg=PALE_YELLOW); f.pack(padx=12, pady=8, fill="x")

        tk.Label(f, text="Nombre de la persona:", font=FONT_LABEL, bg=PALE_YELLOW).grid(row=0, column=0, sticky="w")
        e_nombre = tk.Entry(f, font=FONT_NORMAL, width=30); e_nombre.grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(f, text="Fecha (YYYY-MM-DD):", font=FONT_LABEL, bg=PALE_YELLOW).grid(row=1, column=0, sticky="w")
        if TKCAL:
            e_fecha = DateEntry(f, date_pattern="yyyy-mm-dd", width=12)
            try:
                e_fecha.set_date(prefill_date)
            except:
                pass
        else:
            e_fecha = tk.Entry(f, font=FONT_NORMAL, width=14)
            e_fecha.insert(0, prefill_date)
        e_fecha.grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(f, text="Hora:", font=FONT_LABEL, bg=PALE_YELLOW).grid(row=2, column=0, sticky="w")
        e_hora = ttk.Combobox(f, values=HORAS, state="readonly", width=10); e_hora.set(HORAS[0]); e_hora.grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(f, text="Teléfono:", font=FONT_LABEL, bg=PALE_YELLOW).grid(row=3, column=0, sticky="w")
        e_tel = tk.Entry(f, font=FONT_NORMAL, width=18); e_tel.grid(row=3, column=1, sticky="w", pady=4)

        tk.Label(f, text="Notas:", font=FONT_LABEL, bg=PALE_YELLOW).grid(row=4, column=0, sticky="w")
        e_notas = tk.Entry(f, font=FONT_NORMAL, width=36); e_notas.grid(row=4, column=1, sticky="w", pady=4)

        def crear_persona_action(event=None):
            try:
                nombre = e_nombre.get().strip()
                fecha = e_fecha.get().strip()
                hora = e_hora.get().strip()
                tel = e_tel.get().strip()
                notas = e_notas.get().strip()

                if not nombre or not fecha:
                    messagebox.showwarning("Validación", "Nombre y fecha obligatorios.")
                    return

                try:
                    datetime.strptime(fecha, "%Y-%m-%d")
                except Exception:
                    messagebox.showwarning("Validación", "Fecha inválida. Usa YYYY-MM-DD.")
                    return

                if hora not in HORAS:
                    messagebox.showwarning("Validación", "Selecciona una hora válida.")
                    return

                import re
                if tel and not re.match(r'^[\d\+\-\s\(\)]*$', tel):
                    messagebox.showwarning("Validación", "Teléfono inválido (solo números y símbolos + -()).")
                    return

                nid = citas.agregar_cita_persona(nombre, fecha, hora, tel, confirmado=False, notas=notas)
                if nid is None:
                    messagebox.showinfo("Información", "Ya existe una cita idéntica (no se duplicó).")
                else:
                    messagebox.showinfo("Creado", "Visita creada.")
                win.destroy()
                try:
                    actualizar_events_citas()
                except Exception:
                    pass
                try:
                    mostrar_citas_fecha(cal.get_date() if cal else fecha)
                except Exception:
                    pass

            except Exception as ex:
                tb = traceback.format_exc()
                print("ERROR crear cita persona:\n", tb)
                messagebox.showerror("Error al crear cita", f"Ocurrió un error: {ex}\nRevisa la consola para más detalles.")

        e_nombre.bind("<Return>", lambda e: e_fecha.focus_set())
        e_fecha.bind("<Return>", lambda e: e_hora.focus_set())
        e_hora.bind("<Return>", lambda e: e_tel.focus_set())
        e_tel.bind("<Return>", lambda e: e_notas.focus_set())
        e_notas.bind("<Return>", crear_persona_action)

        tk.Button(win, text="Crear visita persona", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=crear_persona_action).pack(pady=8)

    btn_new.config(command=lambda: nueva_cita_modal(cal.get_date() if cal else datetime.now().strftime("%Y-%m-%d")))

    cols_person = ("Nombre","Fecha","Hora","Telefono","Confirmado","Notas")
    tbl_persons = ttk.Treeview(right, columns=cols_person, show="headings", height=14)
    for c in cols_person: tbl_persons.heading(c, text=c); tbl_persons.column(c, anchor="center", width=110)
    vsb_q = ttk.Scrollbar(right, orient="vertical", command=tbl_persons.yview); tbl_persons.configure(yscroll=vsb_q.set); vsb_q.pack(side="right", fill="y")
    tbl_persons.pack(fill="both", expand=True)
    parent.current_table = tbl_persons

    def llenar_tabla_persons(rows):
        for it in tbl_persons.get_children(): tbl_persons.delete(it)
        for r in rows:
            iid = r.get("ID")
            tbl_persons.insert("", "end", iid=iid, values=(r.get("Nombre"), r.get("Fecha"), r.get("Hora"), r.get("Telefono",""), r.get("Confirmado",""), r.get("Notas","")))

    def mostrar_citas_fecha(date_str):
        datos = citas.citas_por_fecha(date_str)
        persons = [d for d in datos if (d.get("Tipo") or "").upper()!="PERRO"]
        llenar_tabla_persons(persons)

    def actualizar_events_citas():
        if not TKCAL or cal is None: return
        try:
            for ev in cal.get_calevents(): cal.calevent_remove(ev)
        except:
            pass
        for c in citas.leer_citas():
            try:
                if (c.get("Tipo") or "").upper() != "PERRO":
                    label = (c.get("Nombre") or "")[:10]
                    color = "green" if (c.get("Confirmado") or "").lower().startswith("s") else "blue"
                    cal.calevent_create(c.get("Fecha"), label, tags=("cita",), background=color)
            except:
                pass

    if TKCAL and cal is not None:
        cal.bind("<<CalendarSelected>>", lambda e: mostrar_citas_fecha(cal.get_date()))
        actualizar_events_citas()
        hoy = datetime.now().strftime("%Y-%m-%d")
        try: cal.selection_set(hoy)
        except: pass
        mostrar_citas_fecha(hoy)
    else:
        llenar_tabla_persons([c for c in citas.leer_citas() if (c.get("Tipo") or "").upper()!="PERRO"])

    def editar_cita():
        sel = tbl_persons.selection()
        if not sel:
            messagebox.showwarning("Editar","Selecciona una cita."); return
        cid = sel[0]
        rec = next((r for r in citas.leer_citas() if r.get("ID")==cid), None)
        if not rec:
            messagebox.showerror("Error","Registro no encontrado."); return
        win = tk.Toplevel(root); win.title("Editar cita"); win.geometry("480x300"); win.configure(bg=PALE_YELLOW)
        tk.Label(win, text="Editar cita (persona)", font=FONT_TITLE, bg=PALE_YELLOW).pack(pady=8)
        f = tk.Frame(win, bg=PALE_YELLOW); f.pack(padx=12, pady=8, fill="x")
        tk.Label(f, text="Nombre:", bg=PALE_YELLOW).grid(row=0,column=0,sticky="w")
        en = tk.Entry(f); en.insert(0, rec.get("Nombre","")); en.grid(row=0,column=1,sticky="w")
        tk.Label(f, text="Fecha (YYYY-MM-DD):", bg=PALE_YELLOW).grid(row=1,column=0,sticky="w")
        ef = tk.Entry(f); ef.insert(0, rec.get("Fecha","")); ef.grid(row=1,column=1,sticky="w")
        tk.Label(f, text="Hora:", bg=PALE_YELLOW).grid(row=2,column=0,sticky="w")
        eh = ttk.Combobox(f, values=HORAS, state="readonly", width=10); eh.set(rec.get("Hora") or HORAS[0]); eh.grid(row=2,column=1,sticky="w")
        tk.Label(f, text="Teléfono:", bg=PALE_YELLOW).grid(row=3,column=0,sticky="w")
        et = tk.Entry(f); et.insert(0, rec.get("Telefono","")); et.grid(row=3,column=1,sticky="w")
        tk.Label(f, text="Notas:", bg=PALE_YELLOW).grid(row=4,column=0,sticky="w")
        enot = tk.Entry(f); enot.insert(0, rec.get("Notas","")); enot.grid(row=4,column=1,sticky="w")
        var_conf = tk.StringVar(value=rec.get("Confirmado","No"))
        tk.Checkbutton(f, text="Confirmado", variable=var_conf, onvalue="Si", offvalue="No", bg=PALE_YELLOW).grid(row=5,column=1,sticky="w", pady=(8,0))
        def guardar():
            nombre = en.get().strip(); fecha = ef.get().strip(); hora = eh.get().strip()
            tel = et.get().strip(); notas = enot.get().strip(); confirmado = var_conf.get()
            if not nombre or not fecha:
                messagebox.showwarning("Validación","Nombre y fecha requeridos."); return
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except:
                messagebox.showwarning("Validación","Fecha inválida."); return
            if hora not in HORAS:
                messagebox.showwarning("Validación","Hora inválida."); return
            datos = {"Nombre": nombre, "Fecha": fecha, "Hora": hora, "Telefono": tel, "Confirmado": confirmado, "Notas": notas}
            ok = citas.actualizar_cita(cid, datos)
            if ok:
                messagebox.showinfo("Guardado","Cita actualizada.")
                win.destroy()
                actualizar_events_citas(); mostrar_citas_fecha(cal.get_date() if cal else fecha)
            else:
                messagebox.showerror("Error","No se pudo actualizar la cita.")
        tk.Button(win, text="Guardar", bg=BTN_BLUE, fg="white", command=guardar).pack(pady=10)

    btn_edit.config(command=editar_cita)
    def borrar_cita():
        sel = tbl_persons.selection()
        if not sel: messagebox.showwarning("Eliminar","Selecciona una cita."); return
        if not messagebox.askyesno("Confirmar","¿Eliminar cita?"): return
        citas.eliminar_cita(sel[0])
        messagebox.showinfo("Eliminado","Cita eliminada.")
        actualizar_events_citas(); mostrar_citas_fecha(cal.get_date() if cal else datetime.now().strftime("%Y-%m-%d"))
    btn_delete.config(command=borrar_cita)
    def confirmar_sel():
        sel = tbl_persons.selection()
        if not sel: messagebox.showwarning("Confirmar","Selecciona una cita."); return
        citas.confirmar_cita(sel[0])
        messagebox.showinfo("Confirmado","Cita marcada como confirmada.")
        actualizar_events_citas(); mostrar_citas_fecha(cal.get_date() if cal else datetime.now().strftime("%Y-%m-%d"))
    btn_confirm.config(command=confirmar_sel)
    btn_bus.config(command=lambda: llenar_tabla_persons([d for d in citas.buscar_citas_por_nombre(e_bus.get().strip()) if (d.get("Tipo") or "").upper()!="PERRO"]))
    btn_show_all.config(command=lambda: [e_bus.delete(0,tk.END), llenar_tabla_persons([d for d in citas.leer_citas() if (d.get("Tipo") or "").upper()!="PERRO"])])

# ---------------- PANEL REPORTES y CONFIG --------------
def panel_reportes(parent):
    limpiar(parent)
    frm = tk.Frame(parent, bg=TABLE_BG, padx=12, pady=12); frm.pack(fill="both", expand=True)
    tk.Label(frm, text="Reportes mensuales", font=FONT_TITLE, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w")

    hoy = datetime.now()
    años = [str(y) for y in range(hoy.year-3, hoy.year+2)]
    meses = [("01","Enero"),("02","Febrero"),("03","Marzo"),("04","Abril"),("05","Mayo"),("06","Junio"),
            ("07","Julio"),("08","Agosto"),("09","Septiembre"),("10","Octubre"),("11","Noviembre"),("12","Diciembre")]

    sel_frame = tk.Frame(frm, bg=TABLE_BG); sel_frame.pack(pady=10, anchor="w")
    tk.Label(sel_frame, text="Mes:", bg=TABLE_BG, fg=TEXT_COLOR, font=FONT_LABEL).grid(row=0,column=0,padx=6)
    cb_mes = ttk.Combobox(sel_frame, values=[m[1] for m in meses], state="readonly", width=12)
    cb_mes.current(hoy.month-1); cb_mes.grid(row=0,column=1,padx=6)
    tk.Label(sel_frame, text="Año:", bg=TABLE_BG, fg=TEXT_COLOR, font=FONT_LABEL).grid(row=0,column=2,padx=6)
    cb_ano = ttk.Combobox(sel_frame, values=años, state="readonly", width=6); cb_ano.set(str(hoy.year)); cb_ano.grid(row=0,column=3,padx=6)

    def generar_mes():
        m_idx = cb_mes.current() + 1
        y = int(cb_ano.get())
        start = datetime(y, m_idx, 1).strftime("%Y-%m-%d")
        if m_idx == 12:
            end_dt = datetime(y+1, 1, 1) - timedelta(days=1)
        else:
            end_dt = datetime(y, m_idx+1, 1) - timedelta(days=1)
        end = end_dt.strftime("%Y-%m-%d")
        sel = simpledialog.askstring("Formato", "Formato de salida: 'Excel', 'PDF' o 'Ambos'", initialvalue="Ambos")
        if not sel: return
        sel = sel.strip().lower()
        salida_excel = sel in ("excel","ambos")
        salida_pdf = sel in ("pdf","ambos")
        res = reportes.generar_reporte_range(start, end, salida_excel=salida_excel, salida_pdf=salida_pdf)
        if "error" in res:
            messagebox.showerror("Error", res["error"]); return
        texto = f"Noches: {res.get('count_nights',0)}  Extras: {res.get('count_extras',0)}  Anticipos: {res.get('count_anticipos',0)}  Total: ${res.get('total_ingresos',0.0):.2f}"
        if res.get("excel"):
            texto += f"\nExcel: {res['excel']}"
            try: os.startfile(res['excel'])
            except: pass
        if res.get("csv"):
            texto += f"\nCSV: {res['csv']}"
            try: os.startfile(res['csv'])
            except: pass
        if res.get("pdf"):
            texto += f"\nPDF: {res['pdf']}"
            try: os.startfile(res['pdf'])
            except: pass
        messagebox.showinfo("Reporte generado", texto)

    tk.Button(frm, text="Generar reporte del mes seleccionado", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=generar_mes).pack(pady=12)

# ---------------- PANEL CONFIG ----------------
def panel_config(parent):
    limpiar(parent)
    frm = tk.Frame(parent, bg=TABLE_BG, padx=12, pady=12); frm.pack(fill="both", expand=True)
    tk.Label(frm, text="Configuración", font=FONT_TITLE, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w")
    tk.Label(frm, text="Precio por noche (MXN):", font=FONT_LABEL, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
    epre = tk.Entry(frm, font=FONT_NORMAL); epre.insert(0, str(cfg.get("precio_por_noche",250.0))); epre.pack(anchor="w")
    tk.Label(frm, text="Porcentaje de anticipo (%):", font=FONT_LABEL, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
    eant = tk.Entry(frm, font=FONT_NORMAL); eant.insert(0, str(cfg.get("anticipo_porcentaje",30.0))); eant.pack(anchor="w")
    tk.Label(frm, text="Precio guardería por hora (MXN):", font=FONT_LABEL, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
    epre_g = tk.Entry(frm, font=FONT_NORMAL); epre_g.insert(0, str(cfg.get("precio_guarderia_por_hora",50.0))); epre_g.pack(anchor="w")
    tk.Label(frm, text="Porcentaje anticipo guardería (%):", font=FONT_LABEL, bg=TABLE_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
    eant_g = tk.Entry(frm, font=FONT_NORMAL); eant_g.insert(0, str(cfg.get("anticipo_guarderia_porcentaje",30.0))); eant_g.pack(anchor="w")
    def guardar_cfg():
        try:
            cfg["precio_por_noche"] = float(epre.get()); cfg["anticipo_porcentaje"]=float(eant.get())
            cfg["precio_guarderia_por_hora"] = float(epre_g.get()); cfg["anticipo_guarderia_porcentaje"] = float(eant_g.get())
            configuracion.guardar_config(cfg); messagebox.showinfo("Guardado","Configuración guardada.")
        except Exception as e:
            messagebox.showerror("Error","Valores inválidos.")
    tk.Button(frm, text="Guardar configuración", bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=guardar_cfg).pack(pady=12)

# SIDEBAR
for w in list(sidebar.winfo_children()):
    w.destroy()
btn_w = 20
tk.Button(sidebar, text="Registro", width=btn_w, bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=lambda: panel_registro(content_area)).pack(pady=8)
tk.Button(sidebar, text="Citas", width=btn_w, bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=lambda: panel_citas(content_area)).pack(pady=8)
tk.Button(sidebar, text="Recordatorios", width=btn_w, bg=BTN_GREEN, fg="white", font=FONT_NORMAL, command=mostrar_recordatorios).pack(pady=8)
tk.Button(sidebar, text="Reportes", width=btn_w, bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=lambda: panel_reportes(content_area)).pack(pady=8)
tk.Button(sidebar, text="Configuración", width=btn_w, bg=BTN_BLUE, fg="white", font=FONT_NORMAL, command=lambda: panel_config(content_area)).pack(pady=8)
tk.Button(sidebar, text="Salir", width=btn_w, bg=BTN_RED, fg="white", font=FONT_NORMAL, command=root.quit).pack(side="bottom", pady=10)

panel_registro(content_area)

root.mainloop()
