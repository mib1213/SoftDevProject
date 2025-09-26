import pandas as pd
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway # für Prometheus (optional)
from datetime import datetime
import os
import csv
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY ist nicht gesetzt. Bitte in der .env-Datei konfigurieren.")

CSV_COMBINED_FILE = "/Users/omer/Programming/SoftDevProject/Version2/combined_temperature_log_2.csv"
CSV_WIDE_FILE = "/Users/omer/Programming/SoftDevProject/Version2/combined_temperature_wide_2.csv"
PUSHGATEWAY_URL = "localhost:9091"

# Mapping: Stadt → Region (wie in historischen Daten) ===
city_to_region = {
    'Berlin': 'Deutschland',
    'Potsdam': 'Brandenburg',
    'Stuttgart': 'Baden-Wuerttemberg',
    'Munich': 'Bayern',
    'Wiesbaden': 'Hessen',
    'Schwerin': 'Mecklenburg-Vorpommern',
    'Hanover': 'Niedersachsen',
    'Hamburg': 'Niedersachsen/Hamburg/Bremen',
    'Düsseldorf': 'Nordrhein-Westfalen',
    'Mainz': 'Rheinland-Pfalz',
    'Kiel': 'Schleswig-Holstein',
    'Saarbrücken': 'Saarland',
    'Dresden': 'Sachsen',
    'Magdeburg': 'Sachsen-Anhalt',
    'Erfurt': 'Thueringen'
}

registry = CollectorRegistry()
g = Gauge("combined_temperature_celsius", "Temperatur Historisch + Live", ["city", "quelle"], registry=registry)

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
print(f"🔄 Startzeit: {timestamp} UTC")

file_exists = os.path.isfile(CSV_COMBINED_FILE)
live_rows = []

# Live-Daten abrufen
for city, region in city_to_region.items():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},de&appid={API_KEY}&units=metric"
        r = requests.get(url)
        data = r.json()
        temperatur = data["main"]["temp"]
        g.labels(city=region, quelle="live").set(temperatur)
        live_rows.append([timestamp, region, temperatur, "live"])
        print(f"✔ Live-Temperatur {region} ({city}): {temperatur} °C")
    except Exception as e:
        print(f"❌ Fehler bei {city} → {region}: {e}")

# Synthetische Regionen ergänzen (Durchschnitt berechnen)
# Weil wir keine Live-Daten für Brandenburg/Berlin und Thueringen/Sachsen-Anhalt haben
try:
    temp_dict = {row[1]: row[2] for row in live_rows}

    # Brandenburg/Berlin
    if "Brandenburg" in temp_dict and "Deutschland" in temp_dict:
        temp_bb = (temp_dict["Brandenburg"] + temp_dict["Deutschland"]) / 2
        live_rows.append([timestamp, "Brandenburg/Berlin", temp_bb, "live"])
        print(f"➕ Synthetisch Brandenburg/Berlin: {temp_bb} °C")

    # Thueringen/Sachsen-Anhalt
    if "Thueringen" in temp_dict and "Sachsen-Anhalt" in temp_dict:
        temp_ts = (temp_dict["Thueringen"] + temp_dict["Sachsen-Anhalt"]) / 2
        live_rows.append([timestamp, "Thueringen/Sachsen-Anhalt", temp_ts, "live"])
        print(f"➕ Synthetisch Thueringen/Sachsen-Anhalt: {temp_ts} °C")

except Exception as e:
    print(f"⚠️ Fehler beim Erzeugen synthetischer Regionen: {e}")

# Anhängen an Long-CSV
if live_rows:
    with open(CSV_COMBINED_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "city", "temperature", "quelle"])
        writer.writerows(live_rows)
    print("📌 Live-Daten erfolgreich gespeichert.")

# Wide-Format generieren
try:
    df = pd.read_csv(CSV_COMBINED_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df[df["timestamp"].notna()]
    df_wide = df.drop(columns=["quelle"])
    df_wide = df_wide.pivot_table(index="timestamp", columns="city", values="temperature", aggfunc="mean")
    df_wide = df_wide.reset_index()
    df_wide.to_csv(CSV_WIDE_FILE, index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"✔ Wide-Datei '{CSV_WIDE_FILE}' wurde erfolgreich erstellt.")
except Exception as e:
    print(f"❌ Fehler beim Erstellen der Wide-Datei: {e}")

# Falls wir noch Prometheus verwenden wollen, um die Daten zu pushen, können wir so die Daten an den Pushgateway senden:
# Hinweis: Der Pushgateway muss laufen, damit dieser Teil funktioniert.

# Push an Prometheus Pushgateway
# try:
#     push_to_gateway(PUSHGATEWAY_URL, job="combined_temperature_push", registry=registry)
#     print("✔ Push an Pushgateway erfolgreich.")
# except Exception as e:
#     print(f"❌ Fehler beim Push an Pushgateway: {e}")
