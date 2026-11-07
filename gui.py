"""Interfaz gráfica (Tkinter) del simulador."""
import tkinter as tk
from tkinter import ttk, messagebox

from simulador import SimuladorDisco
from escenarios import ESCENARIOS, aplicar_paso


class SimuladorGUI:
    ANCHO_MAXIMO = 560      # ancho máximo del canvas (px)
    ALTO_VISIBLE = 420      # alto visible del canvas (px); si no entra, hay scroll
    CELDA_MAXIMA = 50
    COLOR_LIBRE = "#d9d9d9"
    PALETA = [
        "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
        "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080",
        "#9a6324", "#800000", "#808000", "#000075", "#e6beff",
    ]

    def __init__(self, root):
        self.root = root
        self.disco = None
        self.colores_archivos = {}
        self.pasos_pendientes = []
        self.columnas = 8
        self.celda = self.CELDA_MAXIMA

        izq = ttk.Frame(root, padding=10)
        izq.pack(side=tk.LEFT, fill=tk.BOTH)
        der = ttk.Frame(root, padding=10)
        der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # ---------- Izquierda: mapa + registro ----------
        marco_canvas = ttk.Frame(izq)
        marco_canvas.pack()
        self.canvas = tk.Canvas(marco_canvas, bg="white", highlightthickness=0)
        scroll_c = ttk.Scrollbar(marco_canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll_c.set)
        self.canvas.pack(side=tk.LEFT)
        scroll_c.pack(side=tk.RIGHT, fill=tk.Y)

        marco_reg = ttk.LabelFrame(izq, text="Registro", padding=5)
        marco_reg.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.txt_registro = tk.Text(marco_reg, height=10, width=70, state=tk.DISABLED, wrap=tk.WORD)
        scroll_r = ttk.Scrollbar(marco_reg, orient=tk.VERTICAL, command=self.txt_registro.yview)
        self.txt_registro.configure(yscrollcommand=scroll_r.set)
        self.txt_registro.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_r.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- Derecha: panel Disco ----------
        f_disco = ttk.LabelFrame(der, text="Disco", padding=8)
        f_disco.pack(fill=tk.X)
        ttk.Label(f_disco, text="Bloques:").pack(side=tk.LEFT)
        self.spin_disco = ttk.Spinbox(f_disco, from_=1, to=1024, width=7)
        self.spin_disco.set(64)
        self.spin_disco.pack(side=tk.LEFT, padx=5)
        ttk.Button(f_disco, text="Reiniciar disco", command=self.on_reiniciar).pack(side=tk.LEFT)

        # Panel Crear archivo
        f_crear = ttk.LabelFrame(der, text="Crear archivo", padding=8)
        f_crear.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(f_crear, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.entry_nombre = ttk.Entry(f_crear, width=20)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(f_crear, text="Tamaño (bloques):").grid(row=1, column=0, sticky="w")
        self.entry_tamano = ttk.Spinbox(f_crear, from_=1, to=64, width=18)
        self.entry_tamano.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(f_crear, text="Crear archivo", command=self.on_crear_archivo).grid(
            row=2, column=0, columnspan=2, pady=4)

        # Panel Escenarios
        f_esc = ttk.LabelFrame(der, text="Escenarios", padding=8)
        f_esc.pack(fill=tk.X, pady=(8, 0))
        nombres = list(ESCENARIOS.keys())
        self.combo_esc = ttk.Combobox(f_esc, values=nombres, state="readonly", width=30)
        self.combo_esc.current(0)
        self.combo_esc.pack(fill=tk.X)
        f_btn = ttk.Frame(f_esc)
        f_btn.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(f_btn, text="Cargar", command=self.on_cargar_escenario).pack(side=tk.LEFT)
        ttk.Button(f_btn, text="Siguiente paso", command=self.on_siguiente_paso).pack(side=tk.LEFT, padx=5)
        ttk.Button(f_btn, text="Ejecutar todo", command=self.on_ejecutar_todo).pack(side=tk.LEFT)

        # Tabla de inodos
        f_tabla = ttk.LabelFrame(der, text="Tabla de inodos", padding=8)
        f_tabla.pack(fill=tk.BOTH, expand=True, pady=8)
        self.tree = ttk.Treeview(f_tabla, columns=("archivo", "tamano", "bloques"),
                                 show="headings", height=8)
        self.tree.heading("archivo", text="Archivo")
        self.tree.heading("tamano", text="Tamaño")
        self.tree.heading("bloques", text="Bloques")
        self.tree.column("archivo", width=110)
        self.tree.column("tamano", width=60, anchor="center")
        self.tree.column("bloques", width=200)
        scroll_t = ttk.Scrollbar(f_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_t.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_t.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(der, text="Eliminar seleccionado", command=self.on_eliminar_archivo).pack(pady=(0, 8))

        # Métricas
        f_met = ttk.LabelFrame(der, text="Métricas", padding=8)
        f_met.pack(fill=tk.X)
        self.lbl_ocupacion = ttk.Label(f_met, text="Ocupación: -")
        self.lbl_ocupacion.pack(anchor="w")
        self.lbl_fragmentacion = ttk.Label(f_met, text="Fragmentación: -")
        self.lbl_fragmentacion.pack(anchor="w")
        self.lbl_hueco = ttk.Label(f_met, text="Mayor hueco: -")
        self.lbl_hueco.pack(anchor="w")

        self.nuevo_disco(64)

    # ------------------------------------------------------------------
    def nuevo_disco(self, total):
        self.disco = SimuladorDisco(total)
        self.colores_archivos = {}
        self.columnas = 8 if total <= 64 else 16
        self.celda = min(self.CELDA_MAXIMA, self.ANCHO_MAXIMO // self.columnas)
        filas = -(-total // self.columnas)   # división hacia arriba

        ancho = self.columnas * self.celda
        alto = filas * self.celda
        self.canvas.config(width=ancho, height=min(alto, self.ALTO_VISIBLE),
                           scrollregion=(0, 0, ancho, alto))
        self.canvas.yview_moveto(0)
        self.entry_tamano.config(to=total)

        self.registrar(f"Disco nuevo de {total} bloques")
        self.refrescar()

    def on_reiniciar(self):
        try:
            total = int(self.spin_disco.get())
            if not 1 <= total <= 1024:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El tamaño del disco debe ser un entero entre 1 y 1024.")
            return
        self.pasos_pendientes = []
        self.nuevo_disco(total)

    # ------------------------------------------------------------------
    def refrescar(self):
        self.dibujar_mapa()
        self.actualizar_tabla_inodos()
        self.actualizar_metricas()

    def _color_de(self, nombre):
        if nombre not in self.colores_archivos:
            idx = len(self.colores_archivos) % len(self.PALETA)
            self.colores_archivos[nombre] = self.PALETA[idx]
        return self.colores_archivos[nombre]

    def dibujar_mapa(self):
        self.canvas.delete("all")
        t = self.celda
        for i, ocupante in enumerate(self.disco.bloques):
            fila, col = divmod(i, self.columnas)
            x0, y0 = col * t, fila * t
            color = self.COLOR_LIBRE if ocupante is None else self._color_de(ocupante)
            self.canvas.create_rectangle(x0, y0, x0 + t, y0 + t, fill=color, outline="white")
            if t >= 24:
                self.canvas.create_text(x0 + t // 2, y0 + t // 2, text=str(i),
                                        font=("Arial", 8 if t >= 40 else 7))

    def actualizar_tabla_inodos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for inodo in self.disco.tabla_inodos.values():
            self.tree.insert("", tk.END, values=(
                inodo.nombre, inodo.tam_bloques, ", ".join(map(str, inodo.bloques_asignados))))

    def actualizar_metricas(self):
        m = self.disco.calcular_metricas()
        f = self.disco.calcular_fragmentacion_externa()
        self.lbl_ocupacion.config(
            text=f"Ocupación: {m['porcentaje']:.1f}% ({m['ocupados']}/{m['total']} bloques)")
        self.lbl_fragmentacion.config(text=f"Fragmentación: {f['porcentaje']:.1f}%")
        self.lbl_hueco.config(text=f"Mayor hueco: {f['mayor_hueco']} bloques")

    # ------------------------------------------------------------------
    def on_crear_archivo(self):
        nombre = self.entry_nombre.get().strip()
        try:
            tamano = int(self.entry_tamano.get())
        except ValueError:
            messagebox.showerror("Error", "El tamaño debe ser un número entero.")
            return

        ok, mensaje = self.disco.crear_archivo(nombre, tamano)
        self.registrar(mensaje)
        if ok:
            self.entry_nombre.delete(0, tk.END)
            self.entry_tamano.set(1)
        else:
            messagebox.showwarning("No se pudo crear", mensaje)
        self.refrescar()

    def on_eliminar_archivo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Seleccioná un archivo de la tabla.")
            return
        nombre = str(self.tree.item(seleccion[0], "values")[0])
        ok, mensaje = self.disco.eliminar_archivo(nombre)
        self.registrar(mensaje)
        self.refrescar()

    # ------------------------------------------------------------------
    def on_cargar_escenario(self):
        nombre = self.combo_esc.get()
        total, pasos = ESCENARIOS[nombre]
        self.spin_disco.set(total)
        self.nuevo_disco(total)
        self.pasos_pendientes = list(pasos)
        self.registrar(f"Escenario cargado: {nombre} ({len(pasos)} pasos)")

    def on_siguiente_paso(self):
        if not self.pasos_pendientes:
            self.registrar("No quedan pasos")
            return
        paso = self.pasos_pendientes.pop(0)
        ok, mensaje = aplicar_paso(self.disco, paso)
        f = self.disco.calcular_fragmentacion_externa()
        self.registrar(f"{mensaje} → fragmentación {f['porcentaje']:.1f}%")
        self.refrescar()

    def on_ejecutar_todo(self):
        while self.pasos_pendientes:
            self.on_siguiente_paso()

    # ------------------------------------------------------------------
    def registrar(self, texto):
        self.txt_registro.config(state=tk.NORMAL)
        self.txt_registro.insert(tk.END, texto + "\n")
        self.txt_registro.see(tk.END)
        self.txt_registro.config(state=tk.DISABLED)


def main_gui():
    root = tk.Tk()
    root.title("Simulador de Sistema de Archivos - AE4")
    SimuladorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main_gui()