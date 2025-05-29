import pandas as pd

CSV_FILE = "/Users/omer/Programming/SoftDevProject/data/temperature_historical_data.csv"
CSV_COMBINED_FILE = "/Users/omer/Programming/SoftDevProject/combined_temperature_log_2.csv"

df = pd.read_csv(CSV_FILE)
df.columns = df.columns.str.strip()

df = df[(df["Jahr"] >= 1881) & (df["Jahr"] <= 2025)]

rows = []
for _, row in df.iterrows():
    jahr = int(row["Jahr"])
    monat = int(row["Monat"])
    region = row["Region"]
    temperatur = float(row["Temperatur"])
    datum = f"{jahr}-{monat:02d}-15 00:00:00"
    rows.append([datum, region, temperatur, "historisch"])

df_out = pd.DataFrame(rows, columns=["timestamp", "city", "temperature", "quelle"])

df_out["timestamp"] = pd.to_datetime(df_out["timestamp"], format="%Y-%m-%d %H:%M:%S")

df_out = df_out.sort_values("timestamp")

df_out.to_csv(CSV_COMBINED_FILE, index=False, date_format="%Y-%m-%d %H:%M:%S")

print(f"✔ Datei '{CSV_COMBINED_FILE}' erfolgreich erstellt mit {len(df_out)} Einträgen.")
