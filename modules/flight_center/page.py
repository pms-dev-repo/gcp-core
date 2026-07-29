from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from modules.flight_center.service import (
    build_flight_number,
    lookup_flight,
    search_airlines,
    search_airports,
    search_routes,
)


def _hero() -> None:
    st.markdown(
        """
        <section class="dashboard-hero">
            <div>
                <div class="dashboard-eyebrow">AVIATION REFERENCE</div>
                <h1>✈ Flight Center</h1>
                <p>Search flight numbers, airlines, airports, cities, countries and routes.</p>
            </div>
            <div class="dashboard-property-chip">● OpenFlights</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_flight_lookup() -> None:
    st.subheader("Build a flight number")

    col1, col2, col3 = st.columns([1, 1, 1.2], gap="medium")
    with col1:
        carrier = st.text_input(
            "Airline code",
            placeholder="BA",
            max_chars=3,
            key="flight_center_carrier",
        ).upper()
    with col2:
        number = st.text_input(
            "Flight number",
            placeholder="254",
            max_chars=6,
            key="flight_center_number",
        ).upper()
    with col3:
        st.text_input(
            "Full flight number",
            value=build_flight_number(carrier, number),
            disabled=True,
        )

    direct = st.text_input(
        "Or search a complete flight number",
        placeholder="BA254",
        key="flight_center_direct",
    )

    value = direct or build_flight_number(carrier, number)
    if not value:
        st.info("Enter an airline code and a flight number, or type a complete flight number.")
        return

    result = lookup_flight(value)
    if not result["valid"]:
        st.warning("Use a format such as BA254, AA1841 or AC873.")
        return

    airline = result["airline"]
    st.markdown(f"### {escape(result['full_flight_number'])}")

    if not airline:
        st.warning(
            f"Carrier {result['carrier_code']} was not found in the OpenFlights airline catalogue."
        )
        return

    cols = st.columns(4, gap="medium")
    values = [
        ("Airline", airline.get("name") or "—"),
        ("IATA / ICAO", f"{airline.get('iata_code') or '—'} / {airline.get('icao_code') or '—'}"),
        ("Country", airline.get("country") or "—"),
        ("Callsign", airline.get("callsign") or "—"),
    ]
    for column, (label, value) in zip(cols, values):
        with column:
            st.metric(label, value)

    st.caption(
        "The complete number is assembled by GCP. OpenFlights identifies the carrier, "
        "but does not validate the scheduled flight number or provide live status."
    )


def _render_airlines() -> None:
    col1, col2 = st.columns([2, 1], gap="medium")
    with col1:
        query = st.text_input(
            "Search airline",
            placeholder="British Airways, BA, BAW or SPEEDBIRD",
            key="flight_center_airline_query",
        )
    with col2:
        country = st.text_input(
            "Country",
            placeholder="United Kingdom",
            key="flight_center_airline_country",
        )

    rows = search_airlines(query, country) if query or country else []
    if not rows:
        st.info("Enter an airline name, code, callsign or country.")
        return

    frame = pd.DataFrame(rows).rename(
        columns={
            "name": "Airline",
            "iata_code": "IATA",
            "icao_code": "ICAO",
            "callsign": "Callsign",
            "country": "Country",
            "active": "Active",
        }
    )
    wanted = ["Airline", "IATA", "ICAO", "Callsign", "Country", "Active"]
    st.dataframe(frame[[column for column in wanted if column in frame]], use_container_width=True, hide_index=True)


def _render_airports() -> None:
    col1, col2 = st.columns([2, 1], gap="medium")
    with col1:
        query = st.text_input(
            "Search airport, city or code",
            placeholder="BGI, Bridgetown or Grantley Adams",
            key="flight_center_airport_query",
        )
    with col2:
        country = st.text_input(
            "Country",
            placeholder="Barbados",
            key="flight_center_airport_country",
        )

    rows = search_airports(query, country) if query or country else []
    if not rows:
        st.info("Enter an airport, IATA/ICAO code, city or country.")
        return

    frame = pd.DataFrame(rows).rename(
        columns={
            "name": "Airport",
            "city": "City",
            "country": "Country",
            "iata_code": "IATA",
            "icao_code": "ICAO",
            "timezone": "Timezone",
        }
    )
    wanted = ["Airport", "City", "Country", "IATA", "ICAO", "Timezone"]
    st.dataframe(frame[[column for column in wanted if column in frame]], use_container_width=True, hide_index=True)


def _render_routes() -> None:
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        airline = st.text_input("Airline code", placeholder="BA", key="flight_center_route_airline")
    with col2:
        origin = st.text_input("Origin", placeholder="BGI", key="flight_center_route_origin")
    with col3:
        destination = st.text_input("Destination", placeholder="LHR", key="flight_center_route_destination")

    rows = search_routes(airline, origin, destination) if airline or origin or destination else []
    if not rows:
        st.info("Enter an airline, origin or destination code.")
        return

    frame = pd.DataFrame(rows).rename(
        columns={
            "airline_code": "Airline",
            "source_airport_code": "Origin",
            "destination_airport_code": "Destination",
            "codeshare": "Codeshare",
            "stops": "Stops",
            "equipment": "Equipment",
        }
    )
    wanted = ["Airline", "Origin", "Destination", "Stops", "Codeshare", "Equipment"]
    st.dataframe(frame[[column for column in wanted if column in frame]], use_container_width=True, hide_index=True)


def render(*_args, **_kwargs) -> None:
    _hero()
    flight_tab, airline_tab, airport_tab, route_tab = st.tabs(
        ["Flights", "Airlines", "Airports", "Routes"]
    )

    with flight_tab:
        _render_flight_lookup()
    with airline_tab:
        _render_airlines()
    with airport_tab:
        _render_airports()
    with route_tab:
        _render_routes()
