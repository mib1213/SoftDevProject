# Temperaturdaten Deutschland: Historisch & Live

## Datenquellen

**Historische Daten**  
→ [DWD Klimadaten](https://www.dwd.de/DE/leistungen/cdc/cdc_ueberblick-klimadaten.html)  
- Monatliche Mittelwerte für alle Bundesländer sowie Gesamtdeutschland von 1881 bis 2025.04

**Echtzeitdaten**  
→ [OpenWeather API](https://openweathermap.org/city/2643743)  
- Live-Temperaturen für alle Bundesländer, aktualisiert minütlich

---

## Datenpipeline

1. **`data_cleaning.ipynb`**  
   → verarbeitet Rohdaten zu `temperature_historical_data.csv`

2. **`initialize_combined_log_2.py`**  
   → initialisiert `combined_temperature_log_2.csv` mit bereinigten historischen Daten

3. **`crontab -e` (jede Minute)** ruft automatisch auf:  
   → `push_combined_temperature_2.py`  
   → aktualisiert `combined_temperature_log_2.csv` + erzeugt `combined_temperature_wide_2.csv`

4. **Grafana Dashboard (CSV-Quelle)**  
   → visualisiert `combined_temperature_wide_2.csv`

---

## 📈 Versionen

### Version 1  
- Durchschnittstemperatur pro Monat von 1881.01 bis 2025.04  
- Danach: Live-Temperatur **nur** für Deutschland

### Version 2  
- Temperaturverlauf **aller Bundesländer + Gesamtdeutschland**  
- Zeitraum: 1881.01 bis 2025.04 (DWD Historisch)  
- Danach: Minütlich aktualisierte Live-Daten (OpenWeather API)

---

## Projektdateien

| Datei | Beschreibung |
|-------|--------------|
| `Version2/initialize_combined_log_2.py` | Initialisiert `combined_temperature_log_2.csv` aus den historischen Daten |
| `Version2/push_combined_temperature_2.py` | Holt minütlich Live-Daten per API, aktualisiert Long- & Wide-Format |
| `Version2/crontab_debug_2.log` | Log-Ausgabe der minütlichen Ausführung über `crontab` |
| `Version2/combined_temperature_log_2.csv` | Temperaturdaten im **Long Format** (historisch + live) |
| `Version2/combined_temperature_wide_2.csv` | Temperaturdaten im **Wide Format** (für Grafana) |
| `data/temperature_historical_data.csv` | Bereinigte historische Temperaturdaten (Long Format) |

---

## API Key einrichten

1. `.env` Datei erstellen:
   ```bash
   cp .env.example .env
   ```
2. Öffne `.env` und füge deinen API Key ein:
    ```ini
    OPENWEATHER_API_KEY=dein_api_key
    ```

## Dashboard

- Link zum aktuellen Dashboard: [Version2-Dashboard öffnen](https://snapshots.raintank.io/dashboard/snapshot/l5ajv9zEEbmdeczNUOSRRIR4iEF5tHxj?orgId=0&refresh=5s)