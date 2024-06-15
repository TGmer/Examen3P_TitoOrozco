import requests
import hashlib
import time
import pandas as pd
import sqlite3
import json
from flask import Flask, render_template_string

def obtener_datos_paises():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def procesar_datos_paises(data):
    rows = []
    for country in data:
        name = country.get("name").get("common")
        languages = country.get("languages")
        if languages:
            language_names = ", ".join(languages.values())
            hashed_language = hashlib.sha1(language_names.encode()).hexdigest()
        else:
            language_names = "N/A"
            hashed_language = ""

        start_time = time.time()
        row = {
            "Country": name,
            "Language": hashed_language,
            "Time": round(time.time() - start_time, 4)  # Tiempo en segundos redondeado a 4 decimales
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df

def calcular_metricas(df):
    tiempo_total = df["Time"].sum()
    tiempo_promedio = df["Time"].mean()
    tiempo_minimo = df["Time"].min()
    tiempo_maximo = df["Time"].max()
    
    return tiempo_total, tiempo_promedio, tiempo_minimo, tiempo_maximo

def guardar_en_sqlite_y_json(df):
    conn = sqlite3.connect('countries.db')
    df.to_sql('countries', conn, if_exists='replace', index=False)
    conn.close()
    
    df.to_json('data.json', orient='records')

app = Flask(__name__)

@app.route('/')
def mostrar_tabla():
    conn = sqlite3.connect('countries.db')
    df = pd.read_sql_query("SELECT * FROM countries", conn)
    conn.close()
    
    html = df.to_html(index=False)
    return render_template_string(html)

if __name__ == '__main__':
    data = obtener_datos_paises()
    if data:
        df = procesar_datos_paises(data)
        guardar_en_sqlite_y_json(df)
        tiempo_total, tiempo_promedio, tiempo_minimo, tiempo_maximo = calcular_metricas(df)
        print(f"Tiempo total: {tiempo_total} s")
        print(f"Tiempo promedio: {tiempo_promedio} s")
        print(f"Tiempo mínimo: {tiempo_minimo} s")
        print(f"Tiempo máximo: {tiempo_maximo} s")
        app.run(debug=True)
    else:
        print("Error al obtener los datos de los países.")
