import flet as ft
from supabase import create_client, Client
from datetime import datetime

# === CONFIGURACIÓN DE SUPABASE ===
SUPABASE_URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
# Nota: La clave está bien, pero para producción te recomiendo usar variables de entorno
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Barber App"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F1014"
    page.padding = 20
    # Ajuste para móviles:
    page.window_width = 400
    page.window_height = 800
    
    # Estado de la aplicación
    # Cambiamos Ref por una variable simple para asegurar compatibilidad en el build
    state = {"user_id": None}
    current_barber_name = "ADMIN PANEL"

    # --- VISTA DE LOGIN ---
    def login_view():
        page.clean()
        email_input = ft.TextField(label="Correo Electrónico", border_color="#FACC15")
        pass_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, border_color="#FACC15")
        
        def do_login(e):
            try:
                if not email_input.value or not pass_input.value:
                    raise Exception("Campos vacíos")
                    
                res = supabase.auth.sign_in_with_password({"email": email_input.value, "password": pass_input.value})
                if res.user:
                    state["user_id"] = res.user.id
                    dashboard_view()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Column([
                ft.Text("💈\nADMIN\nPANEL", size=40, weight="bold", color="#FACC15", text_align=ft.TextAlign.CENTER),
                email_input,
                pass_input,
                ft.ElevatedButton("INICIAR SESIÓN", bgcolor="#FACC15", color="#101114", on_click=do_login, width=400)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    # --- VISTA PRINCIPAL (DASHBOARD) ---
    def dashboard_view():
        page.clean()
        turnos_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        recaudacion_text = ft.Text("$0", size=22, weight="bold", color="#4ADE80")

        def cargar_datos():
            try:
                if not state["user_id"]: return
                
                res = supabase.table("Turnos").select("*").eq("barber_id", state["user_id"]).execute()
                data = res.data
                hoy_str = datetime.now().date().isoformat()
                
                turnos_list.controls.clear()
                total_caja = 0
                
                for t in data:
                    # Usamos .get() por seguridad si una columna viene vacía
                    estado = str(t.get('estado', '')).lower()
                    if estado == "pendiente" and t.get('fecha') == hoy_str:
                        card = ft.Container(
                            content=ft.Column([
                                ft.Text(t.get('nombre', 'Sin nombre'), size=18, weight="bold"),
                                ft.Text(f"🕒 {t.get('hora', '--:--')} | {t.get('servicio', 'Corte')}", color="#FACC15"),
                                ft.Row([
                                    ft.ElevatedButton("FINALIZAR", bgcolor="#FACC15", color="#101114", 
                                                     on_click=lambda _, tid=t['id']: finalizar_turno(tid)),
                                    ft.IconButton(ft.icons.MESSAGE, icon_color="green", 
                                                 on_click=lambda _, tel=t.get('telefono'): page.launch_url(f"https://wa.me/{tel}"))
                                ])
                            ]),
                            bgcolor="#16171D", padding=15, border_radius=15, border=ft.border.all(1, "#2D2D35")
                        )
                        turnos_list.controls.append(card)
                    
                    if estado == "completado":
                        total_caja += int(t.get('precio', 0) or 0)
                
                recaudacion_text.value = f"${total_caja}"
                page.update()
            except Exception as e:
                print(f"Error Sync: {e}")

        def finalizar_turno(id_db):
            try:
                supabase.table("Turnos").update({"estado": "Completado", "precio": 1000}).eq("id", id_db).execute()
                cargar_datos()
            except:
                pass

        page.add(
            ft.Row([
                ft.Text(f"💈 {current_barber_name}", size=20, weight="bold", color="#FACC15"),
                ft.IconButton(ft.icons.SETTINGS, icon_color="white")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Turnos de Hoy", size=22, weight="bold"),
            turnos_list,
            ft.Container(
                content=ft.Row([
                    ft.Text("RECAUDACIÓN:", weight="bold"),
                    recaudacion_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10, bgcolor="#101114", border=ft.border.only(top=ft.border.BorderSide(2, "#4ADE80"))
            )
        )
        cargar_datos()

    login_view()

# IMPORTANTE: Para exportar a APK, Flet recomienda esta estructura
if __name__ == "__main__":
    ft.app(target=main)
