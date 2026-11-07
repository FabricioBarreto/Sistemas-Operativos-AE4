"""Modelo del simulador: solo lógica, sin menús ni prints."""


class Inodo:
    def __init__(self, nombre, tam_bloques):
        self.nombre = nombre
        self.tam_bloques = tam_bloques
        self.bloques_asignados = []


class SimuladorDisco:
    def __init__(self, total_bloques):
        if total_bloques <= 0:
            raise ValueError("El disco debe tener al menos 1 bloque")
        self.total_bloques = total_bloques
        self.bloques = [None] * total_bloques   # None = libre, o nombre del archivo
        self.tabla_inodos = {}                  # nombre -> Inodo

    # ------------------------------------------------------------------
    def crear_archivo(self, nombre, tam):
        """Devuelve (ok, mensaje)."""
        if not nombre:
            return False, "El nombre no puede estar vacío"
        if tam <= 0:
            return False, "El tamaño debe ser de al menos 1 bloque"
        if nombre in self.tabla_inodos:
            return False, "Nombre de archivo duplicado: " + nombre

        libres = [i for i, b in enumerate(self.bloques) if b is None]
        if len(libres) < tam:
            return False, (
                "Espacio en disco insuficiente / Bloques agotados "
                f"(pedidos {tam}, libres {len(libres)})"
            )

        inodo = Inodo(nombre, tam)
        for i in libres[:tam]:
            self.bloques[i] = nombre
            inodo.bloques_asignados.append(i)
        self.tabla_inodos[nombre] = inodo
        return True, f"Archivo creado. Bloques: {inodo.bloques_asignados}"

    def eliminar_archivo(self, nombre):
        """Devuelve (ok, mensaje)."""
        if nombre not in self.tabla_inodos:
            return False, "Archivo no encontrado: " + nombre
        inodo = self.tabla_inodos[nombre]
        for i in inodo.bloques_asignados:
            self.bloques[i] = None
        del self.tabla_inodos[nombre]
        return True, f"Archivo eliminado. Bloques liberados: {inodo.bloques_asignados}"

    # ------------------------------------------------------------------
    def calcular_metricas(self):
        ocupados = sum(1 for b in self.bloques if b is not None)
        libres = self.total_bloques - ocupados
        return {
            "total": self.total_bloques,
            "ocupados": ocupados,
            "libres": libres,
            "porcentaje": ocupados / self.total_bloques * 100,
        }

    def mayor_hueco_contiguo(self):
        mayor = actual = 0
        for b in self.bloques:
            if b is None:
                actual += 1
                mayor = max(mayor, actual)
            else:
                actual = 0
        return mayor

    def calcular_fragmentacion_externa(self):
        mayor = self.mayor_hueco_contiguo()
        libres = self.calcular_metricas()["libres"]
        porcentaje = 0 if libres == 0 else (1 - mayor / libres) * 100
        return {"mayor_hueco": mayor, "libres": libres, "porcentaje": porcentaje}