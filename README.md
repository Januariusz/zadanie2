Zadanie 2 – Pipeline GitHub Actions
Autor: Jakub Janusz
Linki

Repozytorium: https://github.com/Januariusz/zadanie2
Obraz GHCR: https://github.com/Januariusz/zadanie2/pkgs/container/weather-app
Cache DockerHub: https://hub.docker.com/r/kjanusz884/weather-app-cache
Uruchomienia pipeline'u: https://github.com/Januariusz/zadanie2/actions


Opis pipeline'u
Pipeline (.github/workflows/docker-build.yml) wykonuje następujące kroki:

Checkout – pobranie kodu źródłowego
QEMU – instalacja emulatorów architektur (wymagane dla arm64 na runnerach x86_64)
Docker Buildx – konfiguracja sterownika dla multi-platform builds
Login do GHCR – uwierzytelnienie przez GITHUB_TOKEN
Login do DockerHub – uwierzytelnienie przez sekrety (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
Build amd64 – budowanie obrazu dla linux/amd64 i załadowanie lokalnie (na potrzeby skanowania)
Skan CVE (Trivy) – skanowanie pod kątem podatności; pipeline przerywany przy CRITICAL/HIGH
Build & Push multi-arch – budowanie dla linux/amd64,linux/arm64 i push do GHCR (tylko po pozytywnym skanie)

Spełnione wymagania
a) Dwie architektury – obraz budowany jednocześnie dla linux/amd64 i linux/arm64 z użyciem Buildx i QEMU:
yamlplatforms: linux/amd64,linux/arm64
b) Cache w DockerHub – eksporter registry w trybie max, zapisujący wszystkie warstwy pośrednie:
yamlcache-from: type=registry,ref=kjanusz884/weather-app-cache:cache
cache-to:   type=registry,ref=kjanusz884/weather-app-cache:cache,mode=max
c) Skan CVE – Trivy (aquasecurity/trivy-action) blokuje pipeline przy wykryciu CRITICAL/HIGH. Wybrany zamiast Docker Scout jako narzędzie open-source niewymagające dodatkowych subskrypcji:
yaml- uses: aquasecurity/trivy-action@master
  with:
    image-ref: weather-app:scan
    exit-code: '1'
    severity: CRITICAL,HIGH

Schemat tagowania
Obraz w GHCR tagowany jako :latest (zawsze wskazuje na najnowszą wersję z master). Cache w DockerHub pod stałym tagiem :cache.

Sekrety
W Settings → Secrets and variables → Actions należy dodać DOCKERHUB_USERNAME i DOCKERHUB_TOKEN. Token GITHUB_TOKEN dostarczany jest automatycznie.

Uruchomienie
Pipeline uruchamia się przy każdym push na master lub ręcznie przez Actions → Run workflow.
