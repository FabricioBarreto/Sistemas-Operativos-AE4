"""
Simulador de sistema de archivos con asignación indexada (tipo inodos).
AE4 / TIFAS - Sistemas Operativos

Cubre RF1-RF7:
  RF1 crear archivos (valida duplicados y espacio)
  RF2 eliminar archivos (libera bloques)
  RF3 mapa de bloques
  RF4 métricas de ocupación
  RF5 fragmentación externa
  RF6 menú interactivo
  RF7 manejo de errores
"""


class Inodo:
    def __init__(self, nombre, tam_bloques):
        self.nombre = nombre
        self.tam_bloques = tam_bloques
        self.bloques_asignados = []  # Lista de índices de bloques en disco


class SimuladorDisco:
    def __init__(self, total_bloques=64):
        self.total_bloques = total_bloques
        # None indica bloque libre, de lo contrario guarda el nombre del archivo
        self.bloques = [None] * total_bloques
        self.tabla_inodos = {}

    # ------------------------------------------------------------------ RF1
    def crear_archivo(self, nombre, tam_bloques):
        # Validaciones (RF7)
        if not nombre or not nombre.strip():
            print("Error: El nombre del archivo no puede estar vacío.")
            return False
        if tam_bloques <= 0:
            print("Error: El tamaño debe ser de al menos 1 bloque.")
            return False
        if nombre in self.tabla_inodos:
            print(f"Error: El archivo '{nombre}' ya existe.")
            return False

        bloques_libres = [i for i, b in enumerate(self.bloques) if b is None]
        if len(bloques_libres) < tam_bloques:
            print(
                f"Error: Espacio en disco insuficiente. "
                f"Pedidos: {tam_bloques}, libres: {len(bloques_libres)}."
            )
            return False

        # Asignación indexada: el inodo guarda la lista de bloques (no
        # necesitan ser contiguos)
        nuevo_inodo = Inodo(nombre, tam_bloques)
        for i in range(tam_bloques):
            idx = bloques_libres[i]
            self.bloques[idx] = nombre
            nuevo_inodo.bloques_asignados.append(idx)

        self.tabla_inodos[nombre] = nuevo_inodo
        print(
            f"Archivo '{nombre}' creado con éxito. "
            f"Bloques asignados: {nuevo_inodo.bloques_asignados}"
        )
        return True

    # ------------------------------------------------------------------ RF2
    def eliminar_archivo(self, nombre):
        if nombre not in self.tabla_inodos:
            print(f"Error: Archivo '{nombre}' no encontrado.")
            return False

        inodo = self.tabla_inodos[nombre]
        for idx in inodo.bloques_asignados:
            self.bloques[idx] = None

        del self.tabla_inodos[nombre]
        print(
            f"Archivo '{nombre}' eliminado. "
            f"Bloques liberados: {inodo.bloques_asignados}"
        )
        return True

    # ------------------------------------------------------------------ RF3
    def mostrar_mapa(self, por_fila=16):
        print("\nMapa del Disco ([O] ocupado, [L] libre):")
        for inicio in range(0, self.total_bloques, por_fila):
            fila = self.bloques[inicio : inicio + por_fila]
            celdas = "".join("[O]" if b else "[L]" for b in fila)
            print(f"  {inicio:>3}-{inicio + len(fila) - 1:<3} {celdas}")

    # ------------------------------------------------------- Mapa gráfico
    def graficar_mapa(self, archivo_salida="mapa_disco.png", columnas=16):
        """Genera un PNG del disco: verde claro = libre, un color por archivo."""
        try:
            import matplotlib

            matplotlib.use("Agg")  # sin ventana: solo guarda la imagen
            import matplotlib.pyplot as plt
            from matplotlib.patches import Patch
        except ImportError:
            print("Error: falta matplotlib. Instalalo con: pip install matplotlib")
            return False

        filas = -(-self.total_bloques // columnas)  # división hacia arriba

        # Un color por archivo (diccionario nombre -> color)
        paleta = plt.get_cmap("tab20").colors
        colores = {
            nombre: paleta[i % len(paleta)]
            for i, nombre in enumerate(self.tabla_inodos)
        }
        color_libre = (0.85, 0.95, 0.85)  # verde claro
        color_vacio = (1.0, 1.0, 1.0)  # celdas sobrantes (si no es múltiplo)

        # Matriz de filas x columnas x RGB
        imagen = [[color_vacio] * columnas for _ in range(filas)]
        for i, dueno in enumerate(self.bloques):
            imagen[i // columnas][i % columnas] = (
                color_libre if dueno is None else colores[dueno]
            )

        fig, ax = plt.subplots(figsize=(columnas * 0.6, filas * 0.6 + 1.5))
        ax.imshow(imagen, aspect="equal")

        # Líneas de grilla entre celdas
        ax.set_xticks([x - 0.5 for x in range(columnas + 1)], minor=True)
        ax.set_yticks([y - 0.5 for y in range(filas + 1)], minor=True)
        ax.grid(which="minor", color="gray", linewidth=0.8)
        ax.tick_params(
            which="both", bottom=False, left=False, labelbottom=False, labelleft=False
        )

        # Número de bloque en el centro de cada celda
        for i in range(self.total_bloques):
            ax.text(
                i % columnas,
                i // columnas,
                str(i),
                ha="center",
                va="center",
                fontsize=8,
            )

        m = self.calcular_metricas()
        ax.set_title(
            f"Mapa del disco - {m['ocupados']} de {m['total']} " f"bloques ocupados"
        )

        # Leyenda
        leyenda = [Patch(facecolor=color_libre, edgecolor="gray", label="Libre")]
        leyenda += [
            Patch(facecolor=c, edgecolor="gray", label=n) for n, c in colores.items()
        ]
        ax.legend(
            handles=leyenda,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.02),
            ncol=min(len(leyenda), 6),
            frameon=False,
        )

        fig.savefig(archivo_salida, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Mapa guardado en {archivo_salida}")
        return True

    # ------------------------------------------------------------------ RF4
    def calcular_metricas(self):
        ocupados = sum(1 for b in self.bloques if b is not None)
        libres = self.total_bloques - ocupados
        porcentaje = (ocupados / self.total_bloques) * 100
        return {
            "total": self.total_bloques,
            "ocupados": ocupados,
            "libres": libres,
            "porcentaje": porcentaje,
        }

    # ------------------------------------------------------------------ RF5
    def mayor_hueco_contiguo(self):
        """Longitud de la mayor secuencia contigua de bloques libres."""
        mayor = actual = 0
        for b in self.bloques:
            if b is None:
                actual += 1
                mayor = max(mayor, actual)
            else:
                actual = 0
        return mayor

    def calcular_fragmentacion(self):
        """
        Fragmentación externa según el enunciado:
        razón = mayor hueco contiguo libre / total de bloques libres.
        Cerca de 1.0: el espacio libre está casi todo junto (poca frag.).
        Cerca de 0.0: el espacio libre está muy disperso (mucha frag.).
        También se informa el índice clásico 1 - razón.
        """
        libres = self.calcular_metricas()["libres"]
        mayor = self.mayor_hueco_contiguo()
        if libres == 0:
            return {"mayor_hueco": 0, "libres": 0, "razon": 0.0, "indice": 0.0}
        razon = mayor / libres
        return {
            "mayor_hueco": mayor,
            "libres": libres,
            "razon": razon,
            "indice": 1 - razon,
        }

    # ------------------------------------------------------------------ RF6
    def mostrar_inodos_y_metricas(self):
        print("\n--- Tabla de inodos ---")
        if not self.tabla_inodos:
            print("  (no hay archivos)")
        for inodo in self.tabla_inodos.values():
            print(
                f"  {inodo.nombre:<12} tam={inodo.tam_bloques:<3} "
                f"bloques={inodo.bloques_asignados}"
            )

        m = self.calcular_metricas()
        f = self.calcular_fragmentacion()
        print("\n--- Métricas de ocupación ---")
        print(f"  Total de bloques : {m['total']}")
        print(f"  Ocupados         : {m['ocupados']}")
        print(f"  Libres           : {m['libres']}")
        print(f"  Ocupación        : {m['porcentaje']:.1f}%")
        print("\n--- Fragmentación externa ---")
        print(f"  Mayor hueco contiguo libre : {f['mayor_hueco']}")
        print(f"  Bloques libres totales     : {f['libres']}")
        print(f"  Razón (hueco/libres)       : {f['razon']:.2f}")
        print(f"  Índice de fragmentación    : {f['indice'] * 100:.1f}%")


def leer_entero(mensaje):
    try:
        return int(input(mensaje))
    except ValueError:
        print("Error: Debés ingresar un número entero.")
        return None


def pedir_total_bloques(por_defecto=64):
    """Pregunta el tamaño del disco al arrancar (Enter = valor por defecto)."""
    while True:
        texto = input(f"Tamaño del disco en bloques [{por_defecto}]: ").strip()
        if texto == "":
            return por_defecto
        try:
            valor = int(texto)
        except ValueError:
            print("Error: Debés ingresar un número entero.")
            continue
        if valor <= 0:
            print("Error: El disco debe tener al menos 1 bloque.")
            continue
        return valor


def menu():
    disco = SimuladorDisco(pedir_total_bloques())
    opciones = """
===== SIMULADOR DE SISTEMA DE ARCHIVOS =====
1. Crear archivo
2. Eliminar archivo
3. Ver mapa de bloques
4. Ver inodos y métricas
5. Ver mapa gráfico (PNG)
6. Salir
"""
    while True:
        print(opciones)
        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            nombre = input("Nombre del archivo: ").strip()
            tam = leer_entero("Tamaño en bloques: ")
            if tam is not None:
                disco.crear_archivo(nombre, tam)
        elif opcion == "2":
            nombre = input("Nombre del archivo a eliminar: ").strip()
            disco.eliminar_archivo(nombre)
        elif opcion == "3":
            disco.mostrar_mapa()
        elif opcion == "4":
            disco.mostrar_inodos_y_metricas()
        elif opcion == "5":
            disco.graficar_mapa()
        elif opcion == "6":
            print("Saliendo del simulador. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Elegí un número del 1 al 6.")


if __name__ == "__main__":
    menu()
