Zadanie 1 – Aplikacja Pogodowa

**Autor:** Jakub Janusz

 Linki

- GitHub:https://github.com/Januariusz/zadanie1
- DockerHub: https://hub.docker.com/r/kjanusz884/weather-app

1. Kod aplikacji (`app.py`)

Aplikacja napisana w języku Python z użyciem frameworka Flask.

from flask import Flask, render_template_string, request
import datetime
import requests
import sys

app = Flask(__name__)


AUTHOR = "Jakub Janusz"
PORT = 5000

#  Wypisanie informacji do logów
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

Zależności (`requirements.txt`)


Flask==3.0.3
requests==2.31.0


2. Plik Dockerfile

Plik wykorzystuje wieloetapowe budowanie obrazu (multi-stage build) w celu minimalizacji rozmiaru finalnego obrazu oraz optymalizacji działania cache'a.

FROM python:3.11-alpine AS builder

WORKDIR /build

# Optymalizacja cache: Kopiujemy najpierw TYLKO plik requirements.txt..
COPY requirements.txt .

# Instalujemy pakiety w osobnym katalogu lokalnym (--user)
RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.11-alpine

# Metadane zgodne ze standardem OCI
LABEL org.opencontainers.image.authors="Jakub Janusz"
LABEL org.opencontainers.image.description="Aplikacja pogodowa"

WORKDIR /app

# Kopiowanie zależności zainstalowanych w Etapie 1
COPY --from=builder /root/.local /root/.local

# Ustawienie PATH, aby Python widział biblioteki pobrane z flagą --user
ENV PATH=/root/.local/bin:$PATH

# Kopiowanie kodu aplikacji
COPY app.py .

# Informacja o porcie
EXPOSE 5000

# Healthcheck weryfikujący co 30 sekund, czy strona główna aplikacji odpowiada poprawnie
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:5000/ || exit 1

# Uruchomienie serwera aplikacji
CMD ["python", "app.py"]


3. Polecenia

a) Budowanie obrazu


docker build -t weather-app .


b) Uruchomienie kontenera


docker run -d -p 5000:5000 --name weather weather-app


Aplikacja dostępna pod adresem: http://localhost:5000

 c) Odczyt logów z uruchomienia
 
 docker logs weather
 
Przykładowy wynik:

Data uruchomienia: 2024-05-04 12:00:00
Autor programu: Jakub Janusz
Port nasłuchiwania TCP: 5000

d) Liczba warstw i rozmiar obrazu

 Rozmiar obrazu
docker images weather-app

Dokładna liczba warstw
docker history weather-app | tail -n +2 | wc -l

