
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
