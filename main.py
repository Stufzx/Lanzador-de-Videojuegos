import flet as ft
import subprocess
import json
import os
import sys
import winshell
import win32com.client

DATA_FILE = "juegos.json"

def main(page: ft.Page):
    
    page.title = "Launcher de juegos"
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.center()
    page.padding = 20
    page.bgcolor = ft.colors.WHITE
    page.window.width = 1280
    page.window.height = 900
    
    def agregar_a_inicio(nombre="Lanzador de Juegos"):
        startup = winshell.startup()  
        ruta_app = sys.executable  
        ruta_acceso_directo = os.path.join(startup, f"{nombre}.lnk")

        if not os.path.exists(ruta_acceso_directo):
            shell = win32com.client.Dispatch("WScript.Shell")
            acceso_directo = shell.CreateShortCut(ruta_acceso_directo)
            acceso_directo.Targetpath = ruta_app
            acceso_directo.WorkingDirectory = os.path.dirname(ruta_app)
            acceso_directo.IconLocation = ruta_app
            acceso_directo.save()
            
    agregar_a_inicio()
    page.fonts = {
        "MiFuente": "Lanzador-de-Videojuegos/fuentes/WinkySans-VariableFont_wght.ttf"
    }
    page.theme = ft.Theme(font_family="MiFuente")

    # Función para cerrar la ventana
    def cerrar_app(e):
        page.window.close()

    # Botón de cierre
    boton_cerrar = ft.IconButton(
        icon=ft.icons.CLOSE,
        tooltip="Cerrar",
        on_click=cerrar_app,
        icon_color=ft.colors.RED,
        icon_size=24,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    # Añadir el botón arriba a la derecha
    page.add(
        ft.Row(
            controls=[boton_cerrar],
            alignment=ft.MainAxisAlignment.END
        )
    )


    scroll_state = {"x": 0}
    juegos = []

    def handle_close(e):
        page.close(dlg_modal)

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Ayuda"),
        content=ft.Text("Imagen Recomendada 1024x1024"),
        actions=[
            ft.TextButton("Cerrar", on_click=handle_close),
           # ft.TextButton("No", on_click=handle_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        #on_dismiss=lambda e: page.add(
           # ft.Text("Modal dialog dismissed"),
        #),
    )

    def mostrar_ayuda(e):
        page.open(dlg_modal)
        #page.update()

    def guardar_juegos():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(juegos, f, indent=4)

    def crear_container_juego(imagen_path="", juego_path=None, titulo=""):
        imagen_juego = ft.Image(
            src=imagen_path,
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(30),
            #alignment=ft.alignment.center,
            
        )
        
        ruta_juego = {"ruta": juego_path}
        titulo_control = ft.TextField(
            value=titulo,
            text_align=ft.TextAlign.CENTER,
            on_change=lambda e: actualizar_info_juego(index),
            width=480,
            border="none",
            hint_text="Titulo del Juego",   
            #border_radius=ft.border_radius.all(10),
            #filled=True,
            #label="Título del juego",
        )

        def actualizar_info_juego(i):
            juegos[i] = {
                "titulo": titulo_control.value,
                "imagen": imagen_juego.src,
                "juego": ruta_juego["ruta"]
            }
            guardar_juegos()

        def subir_imagen(e):
            def on_result(e: ft.FilePickerResultEvent):
                if e.files:
                    imagen_juego.src = e.files[0].path
                    actualizar_info_juego(index)
                    imagen_juego.update()

            picker = ft.FilePicker(on_result=on_result)
            page.overlay.append(picker)
            page.update()
            picker.pick_files(allow_multiple=False)

        def cargar_ruta_juego(e):
            def on_result(e: ft.FilePickerResultEvent):
                if e.files:
                    ruta_juego["ruta"] = e.files[0].path
                    actualizar_info_juego(index)

            picker = ft.FilePicker(on_result=on_result)
            page.overlay.append(picker)
            page.update()
            picker.pick_files(allowed_extensions=["exe"])
        def eliminar_juego(index, contenedor):
            if 0 <= index < len(juegos):
                del juegos[index]
                row.controls.remove(contenedor)
                guardar_juegos()
                row.update()
        def lanzar_juego(e):
            if ruta_juego["ruta"]:
                try:
                    subprocess.Popen(ruta_juego["ruta"])
                except Exception as err:
                    print("Error al ejecutar:", err)

        index = len(juegos)
        juegos.append({
            "titulo": titulo,
            "imagen": imagen_path,
            "juego": juego_path
        })

        contenedor = ft.Container(
            content=ft.Column([
                titulo_control,
                imagen_juego,
                ft.Row([
                    ft.ElevatedButton("Subir imagen", on_click=subir_imagen,style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.DEEP_PURPLE,
            padding=20,
            elevation=5,
            overlay_color=ft.colors.PURPLE_100,
            shape=ft.RoundedRectangleBorder(radius=20),
        ),),
                    ft.ElevatedButton("Cargar juego", on_click=cargar_ruta_juego),
                    ft.ElevatedButton("Eliminar", icon=ft.icons.DELETE, style=ft.ButtonStyle(bgcolor=ft.colors.RED_100),
                                    on_click=lambda e: eliminar_juego(index, contenedor)),
                ])

            ],
                alignment=ft.MainAxisAlignment.CENTER),
            width=350,
            height=500,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.TRANSPARENT,
            border_radius=10,
            margin=5,
            on_click=lanzar_juego,
            animate_scale=ft.Animation(300, "easeInOut")
        )

        def on_hover(e: ft.HoverEvent):
            contenedor.scale = 1.05 if e.data == "true" else 1
            contenedor.update()

        contenedor.on_hover = on_hover
        return contenedor


    row = ft.Row(
        controls=[],
        spacing=10,
    )



    def agregar_juego(e=None):
        nuevo = crear_container_juego()
        row.controls.append(nuevo)
        row.update()
        guardar_juegos()

    def cargar_juegos_guardados():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for juego in data:
                    cont = crear_container_juego(
                        juego.get("imagen", ""),
                        juego.get("juego", ""),
                        juego.get("titulo", "")
                    )
                    row.controls.append(cont)
            row.update()


    scroll_container = ft.Container(
        content=row,
        width=page.width,
        height=700,
    )

    def on_resize(e):
        scroll_container.width = page.width
        scroll_container.update()

    def on_pan_update(e: ft.DragUpdateEvent):
        scroll_state["x"] += e.delta_x
        row.offset = ft.Offset(scroll_state["x"] / 1000, 0)
        row.update()

    gesture = ft.GestureDetector(
        content=scroll_container,
        on_pan_update=on_pan_update,
    )

    page.on_resize = on_resize
    page.add(
        gesture,
        ft.Row([
            ft.ElevatedButton("Añadir juego", icon=ft.icons.ADD, on_click=agregar_juego),
            ft.ElevatedButton("Ayuda", icon=ft.icons.HELP, on_click=mostrar_ayuda),
        ])
    )

    cargar_juegos_guardados()

ft.app(target=main)
