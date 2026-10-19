"""Entrada a la aplicación."""

COLORS = {
    "green": "\x1b[38;2;46;125;50m",
    "light_green": "\x1b[38;2;102;187;106m",
    "dark_brown": "\x1b[38;2;93;64;55m",
    "light_brown": "\x1b[38;2;140;110;99m",
    "orange": "\x1b[38;2;230;81;0m",
    "reset": "\x1b[0m",
}

LOGO_ART = """
               ###       ######   #######  ########   #######
              ## ##     ##    ## ##     ## ##     ## ##     ##
             ##   ##    ##       ##     ## ##     ## ##     ##
            ##     ##   ##       ##     ## ##     ## ##     ##
            #########   ##       ##     ## ##     ## ##     ##
            ##     ##   ##    ## ##     ## ##     ## ##     ##
            ##     ##    ######   #######  ########   #######

######## ######## ##     ## ########  ##          #####  ######## ########
   ##    ##       ###   ### ##     ## ##         ##   ##    ##    ##
   ##    ##       #### #### ##     ## ##        ##     ##   ##    ##
   ##    ######   ## ### ## ########  ##        ##     ##   ##    #####
   ##    ##       ##     ## ##        ##        #########   ##    ##
   ##    ##       ##     ## ##        ##        ##     ##   ##    ##
   ##    ######## ##     ## ##        #######   ##     ##   ##    ########
"""


def _color_key(row: int) -> str:
    """Devuelve el color de la fila `row` del logo.

    Las filas 0-6 son «ACODO» (verde con el centro en verde claro), la 7 está
    en blanco y las 8-14 son «TEMPLATE» (naranja y marrón oscuro).
    """
    if 1 <= row <= 3:
        return "light_green"
    if row <= 7:
        return "green"
    if row <= 10:
        return "orange"
    return "dark_brown"


def print_welcome() -> None:
    """Imprime la bienvenida con el logo en los colores de Acodo."""
    for row, text in enumerate(LOGO_ART.strip("\n").split("\n")):
        print(f"{COLORS[_color_key(row)]}{text}{COLORS['reset']}")


def main() -> None:
    """Función principal."""
    print_welcome()


if __name__ == "__main__":
    main()
