"""Punto de entrada: elige consola o interfaz gráfica."""


def main():
    print("1. Consola")
    print("2. Interfaz gráfica")
    opcion = input("Elegí una opción: ").strip()

    if opcion == "1":
        from cli import main_cli

        main_cli()
    elif opcion == "2":
        from gui import main_gui

        main_gui()
    else:
        print("Opción inválida.")


if __name__ == "__main__":
    main()
