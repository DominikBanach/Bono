# Projekt na przedmiot "Wirtualizacja i Konteneryzacja" 🐋🐋🐋

## Opis ogólny
W ramach projektu stworzyłem konteneryzowany prototyp aplikacji składający się z dwóch kontenerów obsługiwanych przez mechanizm Compose.
Jeden kontener to RESTowe API stworzone przy pomocy framework'a FastAPI w języku Python, a drugi to baza danych PostgreSQL.

API obsługuje dodawanie i odczytywanie z bazy informacji na temat zdarzeń z codziennego życia. Za pomocą żądań wysyłanych do API można dodawać do bazy rodzaje zdarzeń oraz historię zdarzeń wraz z poszczególnymi timestampami.

Planuję w przyszłości stworzyć większy system typu Quantified Self i dodać do niego logikę biznesową pozwalającą na analizę tych szeregów czasowych np. analizę regularności snu, ponieważ interesuję się analizą danych.

Samo API jest w zasadzie bardzo minimalne i mało użyteczne na obecną chwilę. Na potrzeby zaliczenia skupiłem się na szczegółach związanych z tematyką przedmiotu.

## Wykorzystane zagadnienia z wykładów
W projekcie zaimplementowałem dobre praktyki omawiane na wykładach:

* Użycie obrazu bazowego `slim` (mniejszy rozmiar).
* Wykorzystanie flagi `--no-cache-dir` przy instalacji zależności.
* Modyfikacja zmiennych środowiskowych Pythona (`PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`) w celu odchudzenia obrazu i lepszego logowania.
* Użycie pliku `.dockerignore`.
* Zdefiniowanie użytkownika w obrazie (unikanie pracy jako `root`).
* Nieeksponowanie portu bazy danych na zewnątrz (dostępna tylko w sieci kontenerów).
* Ograniczenie uprawnień (`cap_drop`, `security_opt`).
* Zmienne środowiskowe wydzielone do pliku `.env`.
* Healthcheck bazy danych za pomocą `pg_isready`.
* Ograniczenie zasobów (CPU/RAM) w sekcji `deploy`.
* Sieć typu `Bridge`.

## Jak uruchomić?
### ENV
Przykładowa zawartość pliku `.env` niezbędnego do uruchomienia systemu:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=qwerty
POSTGRES_DB=bono_app
DATABASE_URL=postgresql://admin:qwerty@db:5432/bono_app
```

### Docker Compose
Dzięki mechanizmowi Docker Compose wystarczy mieć aktywnego Docker daemona z mechanizmem Compose i wykorzystać polecenie

```bash
    docker compose up --build
```

### Dokumentacja API
Interaktywna dokumentacja jest dostępna po uruchomieniu aplikacji pod adresem lokalnym [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)