from __future__ import annotations

import csv
import hashlib
import io
from typing import Any, Iterable

import requests

from services.database import get_supabase


AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
AIRLINES_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
ROUTES_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"


def _clean(value: Any) -> str | None:
    text = str(value or "").strip()
    return None if text in {"", r"\N"} else text


def _integer(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _number(value: Any) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _download(url: str) -> list[list[str]]:
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    return list(csv.reader(io.StringIO(response.text)))


def _batches(rows: list[dict[str, Any]], size: int = 500) -> Iterable[list[dict[str, Any]]]:
    for index in range(0, len(rows), size):
        yield rows[index:index + size]


def airports() -> list[dict[str, Any]]:
    output = []
    for row in _download(AIRPORTS_URL):
        if len(row) < 14 or _integer(row[0]) is None:
            continue
        output.append({
            "openflights_id": _integer(row[0]),
            "name": _clean(row[1]) or "Unknown airport",
            "city": _clean(row[2]),
            "country": _clean(row[3]),
            "iata_code": _clean(row[4]),
            "icao_code": _clean(row[5]),
            "latitude": _number(row[6]),
            "longitude": _number(row[7]),
            "altitude_ft": _integer(row[8]),
            "utc_offset": _number(row[9]),
            "dst_code": _clean(row[10]),
            "timezone": _clean(row[11]),
            "location_type": _clean(row[12]),
            "source": _clean(row[13]),
        })
    return output


def airlines() -> list[dict[str, Any]]:
    output = []
    for row in _download(AIRLINES_URL):
        if len(row) < 8 or _integer(row[0]) is None:
            continue
        output.append({
            "openflights_id": _integer(row[0]),
            "name": _clean(row[1]) or "Unknown airline",
            "alias": _clean(row[2]),
            "iata_code": _clean(row[3]),
            "icao_code": _clean(row[4]),
            "callsign": _clean(row[5]),
            "country": _clean(row[6]),
            "active": _clean(row[7]) == "Y",
        })
    return output


def routes() -> list[dict[str, Any]]:
    output = []
    for row in _download(ROUTES_URL):
        if len(row) < 9:
            continue
        key_source = "|".join(str(value or "") for value in row[:9])
        output.append({
            "route_key": hashlib.sha1(key_source.encode("utf-8")).hexdigest(),
            "airline_code": _clean(row[0]),
            "airline_id": _integer(row[1]),
            "source_airport_code": _clean(row[2]),
            "source_airport_id": _integer(row[3]),
            "destination_airport_code": _clean(row[4]),
            "destination_airport_id": _integer(row[5]),
            "codeshare": _clean(row[6]) == "Y",
            "stops": _integer(row[7]) or 0,
            "equipment": _clean(row[8]),
        })
    return output


def _upsert(table: str, rows: list[dict[str, Any]], conflict: str) -> int:
    client = get_supabase()
    for batch in _batches(rows):
        client.table(table).upsert(batch, on_conflict=conflict).execute()
    return len(rows)


def sync_all() -> dict[str, int]:
    airport_rows = airports()
    airline_rows = airlines()
    route_rows = routes()

    return {
        "airports": _upsert("openflights_airports", airport_rows, "openflights_id"),
        "airlines": _upsert("openflights_airlines", airline_rows, "openflights_id"),
        "routes": _upsert("openflights_routes", route_rows, "route_key"),
    }
