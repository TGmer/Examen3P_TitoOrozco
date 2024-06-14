import requests
import pandas as pd
import hashlib
import time
import sqlite3
import json

# Paso 1: Obtener datos de la API
response = requests.get('https://restcountries.com/v3.1/all')
countries = response.json()

# Inicializar lista para almacenar datos
data = []

# Paso 2-4: Extraer nombre del idioma, encriptarlo y medir el tiempo
for country in countries:
    if 'languages' in country:
        for lang_code, lang_name in country['languages'].items():
            start_time = time.time()
            # Encriptar el nombre del idioma con SHA1
            lang_hash = hashlib.sha1(lang_name.encode()).hexdigest()
            # Calcular tiempo tomado
            elapsed_time = time.time() - start_time
            # Almacenar los datos
            data.append([country['name']['common'], lang_name, lang_hash, elapsed_time])

# Crear DataFrame
df = pd.DataFrame(data, columns=['Country', 'Language', 'Language_Hash', 'Time'])

# Paso 6: Calcular estadísticas de tiempo
total_time = df['Time'].sum()
average_time = df['Time'].mean()
min_time = df['Time'].min()
max_time = df['Time'].max()

# Agregar estadísticas al DataFrame
stats = pd.DataFrame({
    'Total_Time': [total_time],
    'Average_Time': [average_time],
    'Min_Time': [min_time],
    'Max_Time': [max_time]
})

# Paso 7: Guardar el DataFrame en SQLite
conn = sqlite3.connect('countries.db')
df.to_sql('countries', conn, if_exists='replace', index=False)
stats.to_sql('stats', conn, if_exists='replace', index=False)
conn.close()

# Paso 8: Generar archivo JSON
df.to_json('data.json', orient='records', lines=True)
