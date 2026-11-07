"""Interfaz de consola del simulador."""
from simulador import SimuladorDisco
from escenarios import ESCENARIOS, aplicar_paso

PALETA = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080",
    "#9a6324", "#800000", "#808000", "#000075", "#e6beff",
]


def mostrar_mapa(disco, columnas=8):
    """Mapa de bloques en texto."""
    print("\nMapa de bloques:")
    for i, b in enumerate(disco.bloques):
        etiqueta = "libre" if b is None else str(b)[:6]
        print(f"[{i:>3}:{etiqueta:<6}]", end=" ")
        if (i + 1) % columnas == 0 or i == len(disco.bloques) - 1:
            print()


def mostrar_metricas(disco):
    m = disco.calcular_metricas()
    f = disco.calcular_fragmentacion_externa()
    print(f"\nTotal: {m['total']} | Ocupados: {m['ocupados']} | Libres: {m['libres']}")
    print(f"Ocupación: {m['porcentaje']:.1f}%")
    print(f"Mayor hueco contiguo: {f['mayor_hueco']} bloques")
    print(f"Fragmentación externa: {f['porcentaje']:.1f}%")


def graficar_mapa(disco, ruta="mapa_disco.png", columnas=8):
    """Guarda el mapa de bloques como imagen PNG."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except ImportError:
        print("Falta matplotlib. Instalalo con: pip install matplotlib")
        return

    colores = {n: PALETA[k % len(PALETA)] for k, n in enumerate(disco.tabla_inodos)}
    filas = -(-disco.total_bloques // columnas)
    fig, ax = plt.subplots(figsize=(columnas * 0.9, filas * 0.9 + 1))
    for i, ocupante in enumerate(disco.bloques):
        fila, col = divmod(i, columnas)
        color = "#d9d9d9" if ocupante is None else colores[ocupante]
        ax.add_patch(Rectangle((col, -fila - 1), 1, 1, facecolor=color, edgecolor="white"))
        ax.text(col + 0.5, -fila - 0.5, str(i), ha="center", va="center", fontsize=7)
    ax.set_xlim(0, columnas)
    ax.set_ylim(-filas, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Mapa de bloques del disco")
    if colores:
        handles = [Rectangle((0, 0), 1, 1, facecolor=c) for c in colores.values()]
        ax.legend(handles, colores.keys(), loc="upper left",
                  bbox_to_anchor=(1.01, 1), fontsize=8)
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"Mapa guardado en {ruta}")


def _pedir_entero(texto, defecto=None):
    valor = input(texto).strip()
    if not valor and defecto is not None:
        return defecto
    try:
        return int(valor)
    except ValueError:
        return None


def cargar_escenario(disco_actual):
    """Lista escenarios, crea un disco nuevo y aplica todos los pasos."""
    nombres = list(ESCENARIOS)
    print("\nEscenarios disponibles:")
    for i, n in enumerate(nombres, 1):
        print(f"  {i}. {n}")
    opcion = _pedir_entero("Elegí un escenario: ")
    if opcion is None or not 1 <= opcion <= len(nombres):
        print("Opción inválida.")
        return disco_actual

    nombre = nombres[opcion - 1]
    total, pasos = ESCENARIOS[nombre]
    disco = SimuladorDisco(total)
    print(f"\n== {nombre} (disco de {total} bloques, {len(pasos)} pasos) ==")
    for paso in pasos:
        ok, mensaje = aplicar_paso(disco, paso)
        f = disco.calcular_fragmentacion_externa()
        print(f"{paso[0]} {paso[1]}: {mensaje} → fragmentación {f['porcentaje']:.1f}%")
    return disco


def main_cli():
    total = _pedir_entero("Tamaño del disco en bloques (Enter = 64): ", defecto=64)
    if total is None or total <= 0:
        print("Tamaño inválido, uso 64.")
        total = 64
    disco = SimuladorDisco(total)

    while True:
        print("\n===== Simulador de Sistema de Archivos =====")
        print("1. Crear archivo")
        print("2. Eliminar archivo")
        print("3. Mostrar mapa de bloques")
        print("4. Mostrar métricas y fragmentación")
        print("5. Graficar mapa (PNG)")
        print("6. Cargar escenario de prueba")
        print("0. Salir")
        opcion = input("Opción: ").strip()

        if opcion == "1":
            nombre = input("Nombre: ").strip()
            tam = _pedir_entero("Tamaño (bloques): ")
            if tam is None:
                print("El tamaño debe ser un entero.")
                continue
            print(disco.crear_archivo(nombre, tam)[1])
        elif opcion == "2":
            nombre = input("Nombre del archivo a eliminar: ").strip()
            print(disco.eliminar_archivo(nombre)[1])
        elif opcion == "3":
            mostrar_mapa(disco)
        elif opcion == "4":
            mostrar_metricas(disco)
        elif opcion == "5":
            graficar_mapa(disco)
        elif opcion == "6":
            disco = cargar_escenario(disco)
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main_cli()