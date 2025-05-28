import pandas as pd
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from datetime import datetime, timedelta

# ===========================
# KONFIGURATION
# ===========================
API_KEY = "89fec74f45a3bde1c659eb87cd74880f"
CITIES = ["Berlin"]  # du kannst hier auch mehrere Städte eintragen
CSV_FILE = "data/temperature_historical_data.csv"
PUSHGATEWAY_URL = "localhost:9091"
SIMULIERTES_JAHR = 2024  # wie weit in die „Gegenwart“ du deine historischen Werte spiegeln willst

# ===========================
# Metrik vorbereiten
# ===========================
registry = CollectorRegistry()
g = Gauge("combined_temperature_celsius", "Temperatur Historisch + Live", ["city", "quelle"], registry=registry)

# ===========================
# Historische Daten pushen
# ===========================
df = pd.read_csv(CSV_FILE)
df.columns = df.columns.str.strip()
df = df[df["Jahr"] >= 2000]  # Optional: nur neuere Jahre

for _, row in df.iterrows():
    jahr = int(row["Jahr"])
    monat = int(row["Monat"])
    region = row["Region"]
    temperatur = float(row["Temperatur"])

    # Zeit simulieren: alles in den Bereich von SIMULIERTES_JAHR bringen
    versatz_jahre = SIMULIERTES_JAHR - jahr
    _ = datetime.utcnow() - timedelta(days=versatz_jahre * 365 + (12 - monat) * 30)

    # Pushen (Prometheus ignoriert explizite Zeitstempel)
    g.labels(city=region, quelle="historisch").set(temperatur)

# ===========================
# Live-Daten pushen
# ===========================
for city in CITIES:
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},de&appid={API_KEY}&units=metric"
        r = requests.get(url)
        data = r.json()
        temperatur = data["main"]["temp"]
        g.labels(city=city, quelle="live").set(temperatur)
        print(f"Live-Temperatur für {city}: {temperatur} °C")
    except Exception as e:
        print(f"Fehler beim Abrufen der Live-Daten für {city}: {e}")

# ===========================
# Push an Pushgateway
# ===========================
push_to_gateway(PUSHGATEWAY_URL, job="combined_temperature_push", registry=registry)
print("✔ Historische + Live-Temperaturen erfolgreich gepusht.")
