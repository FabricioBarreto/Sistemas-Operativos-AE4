# Simulador de Sistema de Archivos — AE4 (TIFAS)

**Asignatura:** Sistemas Operativos — Universidad de la Cuenca del Plata
**Sistema operativo analizado:** Linux (Ubuntu 22.04 LTS)
**Autor:** Fabricio Barreto

## Descripción

Simulador en Python de un sistema de archivos con asignación indexada (tipo inodos), inspirado en el esquema de ext4 de Linux. Permite crear y eliminar archivos sobre un disco simulado de bloques, visualizar el mapa de ocupación (en texto y en gráfico), y calcular métricas de ocupación y fragmentación externa.

## Requisitos

- Python 3.10 o superior.
- matplotlib (solo necesario para la opción 5 del menú, "Ver mapa gráfico (PNG)"). El resto del simulador funciona sin esta dependencia.

## Instalación

Se recomienda usar un entorno virtual.

**Windows (cmd / PowerShell):**
```
python -m venv venv
venv\Scripts\activate
pip install matplotlib
```

**Windows (Git Bash):**
```
python -m venv venv
source venv/Scripts/activate
pip install matplotlib
```

## Ejecución

Con el entorno virtual activado:
```
python main.py
```

Esto abre el menú interactivo por consola:
```
===== SIMULADOR DE SISTEMA DE ARCHIVOS =====
1. Crear archivo
2. Eliminar archivo
3. Ver mapa de bloques
4. Ver inodos y métricas
5. Ver mapa gráfico (PNG)
6. Salir
```

- **1. Crear archivo:** pide nombre y tamaño en bloques. Valida nombre vacío, tamaño inválido, nombre duplicado y espacio insuficiente.
- **2. Eliminar archivo:** libera los bloques asignados al archivo indicado.
- **3. Ver mapa de bloques:** muestra en consola el estado de cada bloque (`[O]` ocupado, `[L]` libre), en filas de 16.
- **4. Ver inodos y métricas:** muestra la tabla de inodos (archivo, tamaño, bloques asignados), el porcentaje de ocupación del disco y el índice de fragmentación externa (mayor hueco libre contiguo sobre el total de bloques libres).
- **5. Ver mapa gráfico (PNG):** genera `mapa_disco.png` en la misma carpeta, con un color distinto por archivo, leyenda y numeración de bloques. Requiere matplotlib.
- **6. Salir:** termina el programa.

## Ejemplo de uso (caso de prueba)

Secuencia sugerida para observar el comportamiento ante la fragmentación:

1. Crear `docA.txt` de 4 bloques.
2. Crear `docB.txt` de 4 bloques.
3. Crear `docC.txt` de 4 bloques.
4. Eliminar `docB.txt` (queda un hueco libre en el medio).
5. Crear `docD.txt` de 6 bloques (el simulador lo ubica usando bloques no contiguos, gracias a la asignación indexada).
6. Elegir la opción 4 para ver cómo cambiaron las métricas y la fragmentación, y la opción 5 para verlo graficado.

## Estructura del código

- `Inodo`: representa el descriptor de un archivo (nombre, tamaño, lista de bloques asignados).
- `SimuladorDisco`: modela el disco (lista de bloques) y la tabla de inodos; implementa crear/eliminar archivos, cálculo de métricas y fragmentación, y las dos formas de visualizar el mapa (texto y gráfico).
- `menu()`: interfaz de consola para interactuar con el simulador.
