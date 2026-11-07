import tkinter as tk
from tkinter import ttk, messagebox
from simulador_v1 import SimuladorDisco


class SimuladorGUI:
    COLUMNAS = 8  # bloques por fila en el mapa
    TAM_CELDA = 50  # tamaño en píxeles de cada bloque
    COLOR_LIBRE = "#d9d9d9"

    # Paleta reutilizable (si ya tenés una en graficar_mapa, usá esa)
    PALETA = [
        "#e6194b",
        "#3cb44b",
        "#4363d8",
        "#f58231",
        "#911eb4",
        "#46f0f0",
        "#f032e6",
        "#bcf60c",
        "#fabebe",
        "#008080",
        "#9a6324",
        "#800000",
        "#808000",
        "#000075",
        "#e6beff",
    ]

    def __init__(self, root):
        self.root = root
        self.disco = SimuladorDisco(64)
        self.colores_archivos = {}  # nombre -> color

        # ---------- Panel izquierdo: mapa de bloques ----------
        frame_izq = ttk.Frame(root, padding=10)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH)

        filas = (64 + self.COLUMNAS - 1) // self.COLUMNAS
        self.canvas = tk.Canvas(
            frame_izq,
            width=self.COLUMNAS * self.TAM_CELDA,
            height=filas * self.TAM_CELDA,
            bg="white",
        )
        self.canvas.pack()

        # ---------- Panel derecho ----------
        frame_der = ttk.Frame(root, padding=10)
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Arriba: formulario para crear archivo
        frame_form = ttk.LabelFrame(frame_der, text="Crear archivo", padding=10)
        frame_form.pack(fill=tk.X)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.entry_nombre = ttk.Entry(frame_form, width=20)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_form, text="Tamaño (bloques):").grid(
            row=1, column=0, sticky="w"
        )
        self.entry_tamano = ttk.Spinbox(frame_form, from_=1, to=64, width=18)
        self.entry_tamano.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(
            frame_form, text="Crear archivo", command=self.on_crear_archivo
        ).grid(row=2, column=0, columnspan=2, pady=5)

        # Medio: tabla de inodos
        frame_tabla = ttk.LabelFrame(frame_der, text="Tabla de inodos", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=("archivo", "tamano", "bloques"),
            show="headings",
            height=10,
        )
        self.tree.heading("archivo", text="Archivo")
        self.tree.heading("tamano", text="Tamaño")
        self.tree.heading("bloques", text="Bloques")
        self.tree.column("archivo", width=100)
        self.tree.column("tamano", width=60, anchor="center")
        self.tree.column("bloques", width=200)

        scroll = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(
            frame_der, text="Eliminar seleccionado", command=self.on_eliminar_archivo
        ).pack(pady=5)

        # Abajo: métricas
        frame_metricas = ttk.LabelFrame(frame_der, text="Métricas", padding=10)
        frame_metricas.pack(fill=tk.X)

        self.lbl_ocupacion = ttk.Label(frame_metricas, text="Ocupación: -")
        self.lbl_ocupacion.pack(anchor="w")
        self.lbl_fragmentacion = ttk.Label(frame_metricas, text="Fragmentación: -")
        self.lbl_fragmentacion.pack(anchor="w")
        self.lbl_hueco = ttk.Label(frame_metricas, text="Mayor hueco: -")
        self.lbl_hueco.pack(anchor="w")

        self.refrescar()

    # ------------------------------------------------------------------
    def refrescar(self):
        self.dibujar_mapa()
        self.actualizar_tabla_inodos()
        self.actualizar_metricas()

    # ------------------------------------------------------------------
    def _color_de(self, nombre):
        """Devuelve un color estable para cada archivo."""
        if nombre not in self.colores_archivos:
            idx = len(self.colores_archivos) % len(self.PALETA)
            self.colores_archivos[nombre] = self.PALETA[idx]
        return self.colores_archivos[nombre]

    def dibujar_mapa(self):
        self.canvas.delete("all")
        t = self.TAM_CELDA

        for i, ocupante in enumerate(self.disco.bloques):
            fila = i // self.COLUMNAS
            col = i % self.COLUMNAS
            x0, y0 = col * t, fila * t
            x1, y1 = x0 + t, y0 + t

            # ocupante es None (libre) o el nombre del archivo
            color = self.COLOR_LIBRE if ocupante is None else self._color_de(ocupante)

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white")
            self.canvas.create_text(
                x0 + t // 2, y0 + t // 2, text=str(i), font=("Arial", 8)
            )

    # ------------------------------------------------------------------
    def actualizar_tabla_inodos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for inodo in self.disco.tabla_inodos.values():
            self.tree.insert(
                "",
                tk.END,
                values=(inodo.nombre, inodo.tam_bloques, str(inodo.bloques_asignados)),
            )

    # ------------------------------------------------------------------
    def actualizar_metricas(self):
        m = self.disco.calcular_metricas()
        f = self.disco.calcular_fragmentacion()

        # Ajustá las claves según lo que devuelvan tus métodos
        self.lbl_ocupacion.config(text=f"Ocupación: {m['porcentaje']:.1f}%")
        self.lbl_fragmentacion.config(text=f"Fragmentación: {f['indice'] * 100:.1f}%")
        self.lbl_hueco.config(text=f"Mayor hueco: {f['mayor_hueco']} bloques")

    # ------------------------------------------------------------------
    def on_crear_archivo(self):
        nombre = self.entry_nombre.get().strip()
        try:
            tamano = int(self.entry_tamano.get())
        except ValueError:
            messagebox.showerror("Error", "El tamaño debe ser un número entero.")
            return

        if not nombre:
            messagebox.showerror("Error", "Ingresá un nombre de archivo.")
            return

        ok = self.disco.crear_archivo(nombre, tamano)
        if ok:
            self.entry_nombre.delete(0, tk.END)
            self.entry_tamano.delete(0, tk.END)
        else:
            messagebox.showwarning(
                "No se pudo crear", "No hay espacio suficiente o el nombre ya existe."
            )
        self.refrescar()

    def on_eliminar_archivo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Seleccioná un archivo de la tabla.")
            return

        nombre = self.tree.item(seleccion[0], "values")[0]
        self.disco.eliminar_archivo(nombre)
        self.colores_archivos.pop(nombre, None)
        self.refrescar()


def main_gui():
    root = tk.Tk()
    root.title("Simulador de Sistema de Archivos - AE4")
    SimuladorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main_gui()
