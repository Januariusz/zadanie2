from flask import Flask, render_template_string, request
import datetime
import requests
import sys

app = Flask(__name__)


AUTHOR = "Jakub Janusz"
PORT = 5000

#Wypisanie informacji do logów
start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"Data uruchomienia: {start_time}")
print(f"Autor programu: {AUTHOR}")
print(f"Port nasłuchiwania TCP: {PORT}")
print(f"==============================")
sys.stdout.flush() # Wymuszenie zrzutu bufora, aby logi w Dockerze pojawiły się natychmiast

# Predefiniowana lista miast z ich współrzędnymi geograficznymi
CITIES = {
    "Lublin, Polska": {"lat": 51.2465, "lon": 22.5684},
    "Kapsztad, RPA": {"lat": -33.9249, "lon": 18.4241},
    "Kioto, Japonia": {"lat": 35.0116, "lon": 135.7681}
}

# html
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Aplikacja Pogodowa</title>
</head>
<body style="font-family: sans-serif; padding: 20px;">
    <h2>Wybierz kraj i miasto</h2>
    <form action="/weather" method="get">
        <select name="city">
            {% for city in cities %}
                <option value="{{ city }}" {% if selected_city == city %}selected{% endif %}>{{ city }}</option>
            {% endfor %}
        </select>
        <button type="submit">Sprawdź pogodę</button>
    </form>

    <hr>

    {% if weather %}
        <h3>Aktualna pogoda: {{ selected_city }}</h3>
        <p><strong>Temperatura:</strong> {{ weather.temperature }} °C</p>
        <p><strong>Prędkość wiatru:</strong> {{ weather.windspeed }} km/h</p>
    {% elif error %}
        <p style="color: red;">Wystąpił błąd pobierania danych.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, cities=CITIES.keys(), selected_city=None)

@app.route("/weather")
def weather():
    # Pobranie wybranego miasta z formularza
    selected_city = request.args.get("city")
    weather_data = None

    if selected_city in CITIES:
        coords = CITIES[selected_city]
        # Wywołanie darmowego API Open-Meteo
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
        try:
            response = requests.get(url)
            weather_data = response.json().get("current_weather", {})
        except:
            return render_template_string(HTML_TEMPLATE, cities=CITIES.keys(), error=True)

    return render_template_string(HTML_TEMPLATE, cities=CITIES.keys(), selected_city=selected_city, weather=weather_data)

if __name__ == "__main__":
    # Nasłuchiwanie na wszystkich interfejsach
    app.run(host="0.0.0.0", port=PORT)
