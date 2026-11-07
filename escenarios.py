"""Casos de prueba como datos + función para aplicar un paso."""


def _fragmentacion_alta():
    pasos = [("crear", f"f{i}", 4) for i in range(1, 17)]
    pasos += [("eliminar", f"f{i}") for i in range(1, 16, 2)]
    pasos.append(("crear", "grande.bin", 20))
    return pasos


# nombre -> (tamaño_disco, lista de pasos)
ESCENARIOS = {
    "Caso guía (docA-docD)": (
        64,
        [
            ("crear", "docA", 4),
            ("crear", "docB", 4),
            ("crear", "docC", 4),
            ("eliminar", "docB"),
            ("crear", "docD", 6),
        ],
    ),
    "Fragmentación alta": (64, _fragmentacion_alta()),
    "Casos límite": (
        20,
        [
            ("crear", "a", 10),
            ("crear", "b", 10),  # disco lleno
            ("crear", "c", 1),  # falla: espacio
            ("crear", "a", 1),  # falla: duplicado
            ("eliminar", "zzz"),  # falla: no encontrado
        ],
    ),
    "Caso Colab (18,18%)": (
        20,
        [
            ("crear", "informe.pdf", 4),
            ("crear", "foto.png", 3),
            ("crear", "datos.csv", 2),
            ("eliminar", "foto.png"),
            ("crear", "sistema.bin", 5),
            ("eliminar", "datos.csv"),
        ],
    ),
}


def aplicar_paso(disco, paso):
    """Aplica un paso al disco. Devuelve (ok, mensaje)."""
    if paso[0] == "crear":
        _, nombre, tamano = paso
        return disco.crear_archivo(nombre, tamano)
    if paso[0] == "eliminar":
        _, nombre = paso
        return disco.eliminar_archivo(nombre)
    return False, f"Paso desconocido: {paso[0]}"
