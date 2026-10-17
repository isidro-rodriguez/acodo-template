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


def print_welcome() -> None:
    """Imprime la bienvenida."""
    lines = LOGO_ART.strip("\n").split("\n")
    for i, row in enumerate(lines):
        if 1 <= i <= 3:
            color_key = "light_green"
        elif 0 <= i <= 7:
            color_key = "green"
        elif 9 <= i <= 11:
            color_key = "orange"
        elif 11 <= i <= 14:
            color_key = "dark_brown"
        else:
            color_key = "light_brown"

        print(f"{COLORS[color_key]}{row}{COLORS['reset']}")


def main() -> None:
    """Función principal."""
    print_welcome()


if __name__ == "__main__":
    main()
