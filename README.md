# Westeros Travel Guide API

A tiny HTTP service that returns a fast fact about iconic places in the Seven Kingdoms
(King's Landing, Winterfell, The Wall and more). Locations are a hardcoded dictionary,
so there is no database. Built with Python 3 and only the standard library.

## What it does

| Endpoint | Response |
|---|---|
| `GET /` | Greeting |
| `GET /healthz` | `200` `{"status": "ok"}` (no database, instant) |
| `GET /locations` | List of available location slugs |
| `GET /locations/<slug>` | Name, region and a fast fact; `404` if unknown |

Example: `curl localhost:8080/locations/the-wall`

## How to run

Requires Python 3.8+. No dependencies to install.

```bash
./scripts/run.sh
```

## Port

The service listens on the `PORT` environment variable and defaults to **8080**.

```bash
PORT=9000 ./scripts/run.sh
```

## How to test

```bash
./scripts/test.sh
```

Exits 0 on success and prints a normalised summary line such as `TESTS: 7/7`.
The tests start the real server and call it over HTTP.

## Project layout

- `app.py` - HTTP server and routing
- `locations.py` - the hardcoded Westeros data
- `tests/test_app.py` - tests
- `scripts/run.sh`, `scripts/test.sh` - the course contract
