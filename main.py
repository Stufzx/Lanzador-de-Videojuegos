import flet as ft
import subprocess
import json
import os
import sys
import winshell 
import win32com.client
from flet import PopupMenuButton, PopupMenuItem, icons
import subprocess
import asyncio
import threading
import time
from playsound import playsound
import pygame


DATA_FILE = "juegos.json"

def main(page: ft.Page):
    
    page.title = "Nexxo"
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.center()
    page.padding = 20
    page.bgcolor = ft.colors.WHITE
    page.window.width = 1280
    page.window.height = 900
    page.window.resizable = False
    # Inicializar mixer de pygame
    pygame.mixer.init()

    # Variables de estado
    musica_actual = {"ruta": None, "nombre": None, "reproduciendo": False}
    page.bgcolor = "#1E1E2F"  # Fondo general oscuro
    page.theme_mode = ft.ThemeMode.DARK  # Establece el modo oscuro

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#00E6C3",        # Color primario
            secondary="#E057B0",      # Color secundario
            on_background="#FFFFFF",  # Fuente blanca por defecto
            background="#1E1E2F"      # Fondo oscuro
        ),
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(color=ft.colors.WHITE),  # Blanco para texto normal
            title_medium=ft.TextStyle(color=ft.colors.WHITE),  # Blanco para títulos
        )
    )


    page.fonts = {
        "MiFuente": "fuentes\WinkySans-VariableFont_wght.ttf"
    }
    page.theme = ft.Theme(font_family="MiFuente")

        # Crear el selector de archivos al iniciar la app
    file_picker = ft.FilePicker(
        on_result=lambda result: print(f"🎵 Música seleccionada: {result.files[0].path}") if result.files else None
    )
    page.overlay.append(file_picker)
    page.update()

    scroll_container = ft.Container(
        content=ft.Row(
            controls=[],
            spacing=10,
        ),
        width=page.width,
        height=700,
    )



    area_arrastre = ft.WindowDragArea(
        ft.Container(
            bgcolor=ft.colors.TRANSPARENT,
            padding=10,
            width=1280,
            
            
        ),
        maximizable=False  # Evita maximizar al hacer doble clic
    )
    page.add(
        ft.Row(
            controls=[area_arrastre],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )
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

    auto_scroll_activo = [False]
    inactividad_timer = [None]
    tiempo_inactivo = 20  # segundos

    def volver_scroll_al_inicio():
        scroll_state["x"] = 0
        row.scroll_to(
            offset=ft.Offset(0, 0),
            duration=500  # milisegundos → más alto = más lento
        )
        row.update()


    def iniciar_autoscroll():
        if auto_scroll_activo[0]:
            return
        auto_scroll_activo[0] = True

        def volver():
            volver_scroll_al_inicio()
            auto_scroll_activo[0] = False

        threading.Thread(target=volver, daemon=True).start()

    def detener_autoscroll():
        auto_scroll_activo[0] = False

    def reiniciar_temporizador_inactividad():
        detener_autoscroll()
        if inactividad_timer[0]:
            inactividad_timer[0].cancel()

        timer = threading.Timer(tiempo_inactivo, iniciar_autoscroll)
        inactividad_timer[0] = timer
        timer.start()

   
    page.on_mouse_move = lambda e: reiniciar_temporizador_inactividad()
    page.on_click = lambda e: reiniciar_temporizador_inactividad()
    page.on_scroll = lambda e: reiniciar_temporizador_inactividad()

    # Iniciar temporizador desde el principio
    reiniciar_temporizador_inactividad()



    def desplazar_scroll():
        scroll_state["x"] += 2  # cantidad de desplazamiento
        row.scroll_to(offset=scroll_state["x"], duration=100)

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

    def filtrar_juegos(texto):
        texto = texto.lower().strip()
        for i, control in enumerate(row.controls):
            if texto in juegos[i]["titulo"].lower():
                control.visible = True
            else:
                control.visible = False
        row.update()


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
            width=350,
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
                    comando = f'Start-Process -FilePath "{ruta_juego["ruta"]}" -Verb runAs'
                    subprocess.run(["powershell", "-Command", comando])
                except Exception as err:
                    print("Error al ejecutar:", err)


        index = len(juegos)
        juegos.append({
            "titulo": titulo,
            "imagen": imagen_path,
            "juego": juego_path
        })

        acciones_menu = ft.PopupMenuButton(
            icon=icons.MORE_VERT,
            items=[
                ft.PopupMenuItem(
                    text="Subir imagen",
                    on_click=subir_imagen
                ),
                ft.PopupMenuItem(
                    text="Cargar juego",
                    on_click=cargar_ruta_juego
                ),
                ft.PopupMenuItem(
                    text="Eliminar",
                    on_click=lambda e: eliminar_juego(index, contenedor),
                    icon=icons.DELETE,
                ),
            ]
        )

        contenedor = ft.Container(
            content=ft.Column(
                [
                    titulo_control,
                    imagen_juego,
                    ft.Row([acciones_menu], alignment=ft.MainAxisAlignment.END),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
            width=350,
            height=450,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.TRANSPARENT,  
            border_radius=10,
            margin=15,
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


    row = ft.Row(
        controls=[],
        spacing=10,
        expand=True,
        scroll=ft.ScrollMode.ALWAYS  # Solo scroll
        
    )

    scroll_container = ft.Container(
        content=row,
        expand=True,
        height=700,
    )


    def cargar_musica(e):
        def on_result(result: ft.FilePickerResultEvent):
            if result.files:
                ruta = result.files[0].path
                nombre = os.path.basename(ruta)

                musica_actual["ruta"] = ruta
                musica_actual["nombre"] = nombre
                musica_actual["reproduciendo"] = False

                texto_musica.value = f"🎶 {nombre}"
                boton_play.icon = ft.icons.PLAY_ARROW
                texto_musica.update()
                boton_play.update()
        
        # Crear file_picker como control global o dentro de la función principal
        file_picker = ft.FilePicker(on_result=on_result)

        # AÑADIRLO a la página antes de actualizarlo o usarlo
        if file_picker not in page.overlay:
            page.overlay.append(file_picker)
            page.update()  # <– Actualiza la página para reflejar cambios

        file_picker.pick_files(allowed_extensions=["mp3"], allow_multiple=False)

    def toggle_reproduccion(e):
        if musica_actual["ruta"] is None:
            return

        if not musica_actual["reproduciendo"]:
            pygame.mixer.music.load(musica_actual["ruta"])
            pygame.mixer.music.play()
            musica_actual["reproduciendo"] = True
            boton_play.icon = ft.icons.PAUSE
        else:
            pygame.mixer.music.stop()
            musica_actual["reproduciendo"] = False
            boton_play.icon = ft.icons.PLAY_ARROW

        boton_play.update()

    # Elementos de interfaz
    boton_cargar = ft.IconButton(
        icon=ft.icons.MUSIC_NOTE,
        tooltip="Cargar música",
        on_click=cargar_musica,
        icon_color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            padding=10
        )
    )

    texto_musica = ft.Text(
        value="No hay música cargada",
        color=ft.colors.WHITE,
        size=14
    )

    boton_play = ft.IconButton(
        icon=ft.icons.PLAY_ARROW,
        tooltip="Reproducir / Pausar",
        on_click=toggle_reproduccion,
        icon_color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            padding=10
        )
    )

    # Añádelo debajo del buscador o donde quieras colocarlo
    barra_musica = ft.Row(
        controls=[boton_cargar, texto_musica, boton_play],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )





    boton_musica = ft.IconButton(
        icon=ft.icons.MUSIC_NOTE,
        tooltip="Cargar música",
        on_click=cargar_musica,
        icon_color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            padding=10
        )
    )


    # Campo de búsqueda
    buscador = ft.TextField(
        hint_text="Buscar juego...",
        width=400,
        prefix_icon=ft.icons.SEARCH,
        on_change=lambda e: filtrar_juegos(e.control.value)
    )

    # Adaptar scroll al tamaño de la ventana
    def on_resize(e):
        scroll_container.width = page.width
        scroll_container.update()

    page.on_resize = on_resize


    
    page.add(
        ft.Column([
            buscador,
            ft.Row([barra_musica], alignment=ft.MainAxisAlignment.START),
            scroll_container,
            ft.Row(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.ADD, color="#00E6C3", size=20),
                                ft.Text("Añadir juego", color="#FFFFFF", weight="bold", size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        bgcolor="#29293d",  # Botón oscuro
                        border=ft.border.all(1.5, "#00E6C3"),  # Borde turquesa
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=22, vertical=12),
                        on_click=agregar_juego,
                        animate=ft.animation.Animation(300, "easeInOut"),
                        ink=True
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.HELP, color="#E057B0", size=20),
                                ft.Text("Ayuda", color="#FFFFFF", weight="bold", size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        bgcolor="#29293d",
                        border=ft.border.all(1.5, "#E057B0"),  # Borde fucsia
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=22, vertical=12),
                        on_click=mostrar_ayuda,
                        animate=ft.animation.Animation(300, "easeInOut"),
                        ink=True
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        expand=True)
    )







    cargar_juegos_guardados()

ft.app(target=main)
