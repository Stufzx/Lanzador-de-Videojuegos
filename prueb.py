import flet as ft

def main(page: ft.Page):
    page.title = "Aplicación con Botón de Cierre"
    page.window_width = 400
    page.window_height = 300
    page.window_title_bar_hidden = True  # Oculta la barra de título del sistema

    # Botón "X" para cerrar la aplicación
    boton_cerrar = ft.IconButton(
        icon=ft.icons.CLOSE,
        tooltip="Cerrar",
        on_click=lambda e: page.window.close(),  # Cierra la aplicación
        icon_color=ft.colors.RED,
        icon_size=20,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    # Área de arrastre para mover la ventana
    area_arrastre = ft.WindowDragArea(
        ft.Container(
            content=ft.Text("Arrastra aquí para mover la ventana"),
            bgcolor=ft.colors.GREY_300,
            padding=10,
        ),
        maximizable=False  # Evita maximizar al hacer doble clic
    )

    # Fila que contiene el área de arrastre y el botón de cierre
    barra_superior = ft.Row(
        controls=[area_arrastre, boton_cerrar],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.add(
        ft.Column([
            barra_superior,
            ft.Text("Contenido de la aplicación...")
        ])
    )

ft.app(target=main)
