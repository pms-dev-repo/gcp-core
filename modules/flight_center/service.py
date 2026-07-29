from __future__ import annotations

import re
from typing import Any

from services.database import get_supabase


FLIGHT_PATTERN = re.compile(r"^([A-Z0-9]{2,3})\s*[- ]?\s*(\d{1,5}[A-Z]?)$")


def normalize_code(value: Any) -> str:
    return str(value or "").strip().upper()


def build_flight_number(carrier_code: Any, flight_number: Any) -> str:
    carrier = normalize_code(carrier_code)
    number = normalize_code(flight_number).replace(" ", "")

    if not carrier:
        return number
    if number.startswith(carrier):
        return number
    return f"{carrier}{number}"


def split_flight_number(value: Any) -> tuple[str, str]:
    normalized = normalize_code(value).replace(" ", "")
    match = FLIGHT_PATTERN.fullmatch(normalized)
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def find_airline_by_code(code: str) -> dict[str, Any] | None:
    code = normalize_code(code)
    if not code:
        return None

    client = get_supabase()
    for column in ("iata_code", "icao_code"):
        response = (
            client.table("openflights_airlines")
            .select("*")
            .eq(column, code)
            .limit(1)
            .execute()
        )
        if response.data:
            return dict(response.data[0])
    return None


def search_airlines(query: str = "", country: str = "", limit: int = 100) -> list[dict[str, Any]]:
    client = get_supabase()
    request = client.table("openflights_airlines").select("*").eq("active", True)

    query = str(query or "").strip()
    country = str(country or "").strip()

    if query:
        safe = query.replace(",", " ")
        request = request.or_(
            f"name.ilike.%{safe}%,iata_code.ilike.%{safe}%,"
            f"icao_code.ilike.%{safe}%,callsign.ilike.%{safe}%"
        )
    if country:
        request = request.ilike("country", f"%{country}%")

    response = request.order("name").limit(limit).execute()
    return [dict(row) for row in (response.data or [])]


def search_airports(query: str = "", country: str = "", limit: int = 100) -> list[dict[str, Any]]:
    client = get_supabase()
    request = client.table("openflights_airports").select("*")

    query = str(query or "").strip()
    country = str(country or "").strip()

    if query:
        safe = query.replace(",", " ")
        request = request.or_(
            f"name.ilike.%{safe}%,city.ilike.%{safe}%,country.ilike.%{safe}%,"
            f"iata_code.ilike.%{safe}%,icao_code.ilike.%{safe}%"
        )
    if country:
        request = request.ilike("country", f"%{country}%")

    response = request.order("name").limit(limit).execute()
    return [dict(row) for row in (response.data or [])]


def search_routes(
    airline_code: str = "",
    origin: str = "",
    destination: str = "",
    limit: int = 100,
) -> list[dict[str, Any]]:
    client = get_supabase()
    request = client.table("openflights_routes").select("*")

    if airline_code:
        request = request.eq("airline_code", normalize_code(airline_code))
    if origin:
        request = request.eq("source_airport_code", normalize_code(origin))
    if destination:
        request = request.eq("destination_airport_code", normalize_code(destination))

    response = request.limit(limit).execute()
    return [dict(row) for row in (response.data or [])]


def lookup_flight(value: str) -> dict[str, Any]:
    carrier_code, flight_number = split_flight_number(value)
    if not carrier_code:
        return {
            "valid": False,
            "full_flight_number": normalize_code(value),
            "carrier_code": "",
            "flight_number": "",
            "airline": None,
        }

    return {
        "valid": True,
        "full_flight_number": build_flight_number(carrier_code, flight_number),
        "carrier_code": carrier_code,
        "flight_number": flight_number,
        "airline": find_airline_by_code(carrier_code),
    }
