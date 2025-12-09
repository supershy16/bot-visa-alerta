import requests
import time
import datetime
import os

TOKEN = os.getenv("TOKEN")  # No pongas el token aquí
CHAT_ID = os.getenv("CHAT_ID")  # Tampoco el chat ID aquí

URL = "https://ais.usvisa-info.com/es-pe/niv/users/sign_in"

ultimo_cambio = None

def enviar_telegram(mensaje):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": mensaje}
    )
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": "🔔🔔🔔 ALERTA 🔔🔔🔔"}
    )

def detectar_cambios():
    global ultimo_cambio

    try:
        r = requests.get(URL, timeout=10)
        actual = r.headers.get("Date", "")

        if ultimo_cambio and actual != ultimo_cambio:
            ahora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            mensaje = (
                "⚠️ Posible liberación de citas detectada\n\n"
                "🎯 Objetivo: Fechas enero – abril\n"
                "⏳ Revisa tu cuenta AHORA.\n"
                f"🔎 Evento registrado a las: {ahora} UTC\n\n"
                "➡ Entra a tu panel y presiona 'Reprogramar cita'."
            )
            enviar_telegram(mensaje)

        ultimo_cambio = actual

    except Exception as e:
        print("Error:", e)

while True:
    detectar_cambios()
    time.sleep(180)  # Cada 3 minutos
