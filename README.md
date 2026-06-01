# Zadanie 2 – Pipeline GitHub Actions

**Autor:** Jakub Janusz

## Linki

| | |
|---|---|
| Repozytorium | https://github.com/Januariusz/zadanie2 |
| Obraz GHCR | https://github.com/Januariusz/zadanie2/pkgs/container/weather-app |
| Cache DockerHub | https://hub.docker.com/r/kjanusz884/weather-app-cache |
| Uruchomienia pipeline'u | https://github.com/Januariusz/zadanie2/actions |

---

## Opis pipeline'u

Pipeline (`.github/workflows/docker-build.yml`) wykonuje następujące kroki:

| Krok | Opis |
|---|---|
| Checkout | Pobranie kodu źródłowego |
| QEMU | Instalacja emulatorów architektur (wymagane dla `arm64` na runnerach `x86_64`) |
| Docker Buildx | Konfiguracja sterownika dla multi-platform builds |
| Login do GHCR | Uwierzytelnienie przez `GITHUB_TOKEN` |
| Login do DockerHub | Uwierzytelnienie przez sekrety (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`) |
| Build amd64 | Budowanie obrazu dla `linux/amd64` i załadowanie lokalnie (na potrzeby skanowania) |
| Skan CVE (Trivy) | Skanowanie pod kątem podatności; pipeline przerywany przy `CRITICAL`/`HIGH` |
| Build & Push multi-arch | Budowanie dla `linux/amd64,linux/arm64` i push do GHCR (tylko po pozytywnym skanie) |

---

## Spełnione wymagania

### a) Dwie architektury

Obraz budowany jednocześnie dla `linux/amd64` i `linux/arm64` z użyciem Buildx i QEMU:

```yaml
platforms: linux/amd64,linux/arm64
```

### b) Cache w DockerHub

Eksporter `registry` w trybie `max`, zapisujący wszystkie warstwy pośrednie:

```yaml
cache-from: type=registry,ref=kjanusz884/weather-app-cache:cache
cache-to:   type=registry,ref=kjanusz884/weather-app-cache:cache,mode=max
```

### c) Skan CVE

Trivy (`aquasecurity/trivy-action`) blokuje pipeline przy wykryciu `CRITICAL`/`HIGH`.
Wybrany zamiast Docker Scout jako narzędzie open-source niewymagające dodatkowych subskrypcji:

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: weather-app:scan
    exit-code: '1'
    severity: CRITICAL,HIGH
```

---

## Schemat tagowania

| Zasób | Tag | Opis |
|---|---|---|
| Obraz (GHCR) | `:latest` | Zawsze wskazuje na najnowszą wersję z `master` |
| Cache (DockerHub) | `:cache` | Stały tag dla eksportera `registry` |

---

## Sekrety

W **Settings → Secrets and variables → Actions** należy skonfigurować:

| Sekret | Opis |
|---|---|
| `DOCKERHUB_USERNAME` | Login użytkownika DockerHub |
| `DOCKERHUB_TOKEN` | Access Token DockerHub (nie hasło) |

> `GITHUB_TOKEN` dostarczany jest automatycznie przez GitHub Actions.

---

## Uruchomienie

Pipeline uruchamia się automatycznie przy każdym `push` na gałąź `master`
lub ręcznie przez **Actions → Run workflow**.
