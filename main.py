import requests
import time
import datetime
import os
import random

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://ais.usvisa-info.com/es-pe/niv/users/sign_in"

ultimo_cambio = None
ultimo_alerta_suave = 0
ultimo_alerta_fuerte = 0
cambios_consecutivos = 0

def enviar_telegram(mensaje):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": mensaje}
    )

def hora_valida():
    """Permite solo horarios donde hay movimiento real (8–12 y 16–20)"""
    peru_hour = datetime.datetime.utcnow().hour - 5
    if peru_hour < 0:
        peru_hour += 24

    if 8 <= peru_hour <= 12:
        return True
    if 16 <= peru_hour <= 20:
        return True

    return False

def detectar_cambios():
    global ultimo_cambio, cambios_consecutivos
    global ultimo_alerta_suave, ultimo_alerta_fuerte

    try:
        r = requests.get(URL, timeout=10)
        actual = r.headers.get("Date", "")

        # Solo procesar en horario útil
        if not hora_valida():
            return

        # Detecta cambio en el header "Date"
        if ultimo_cambio and actual != ultimo_cambio:
            cambios_consecutivos += 1
            ahora = int(time.time())

            # ------------------------------
            # 🔵 ALERTA SUAVE
            # ------------------------------
            if ahora - ultimo_alerta_suave > 180:  # mínimo 3 minutos entre alertas suaves
                enviar_telegram("🔵 *Movimiento detectado en el sistema de citas*\nRevisa si hay cambios.")
                ultimo_alerta_suave = ahora

            # ------------------------------
            # 🔴 ALERTA FUERTE
            # ------------------------------
            if cambios_consecutivos >= 2 and (ahora - ultimo_alerta_fuerte > 300):
                enviar_telegram("🔴 *Cambio FUERTE detectado*\nAlta probabilidad de nuevas fechas.\nRevisa YA tu cuenta.")
                ultimo_alerta_fuerte = ahora
                cambios_consecutivos = 0

        else:
            cambios_consecutivos = 0

        ultimo_cambio = actual

    except Exception as e:
        print("Error:", e)

# Mensaje al iniciar el bot
enviar_telegram("🔵 El bot inteligente V2 inició correctamente. Monitoreando en horarios útiles...")

while True:
    detectar_cambios()

    # Espera aleatoria entre 160–220 segundos para no generar patrones fijos
    time.sleep(random.randint(160, 220))
