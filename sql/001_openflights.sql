create table if not exists public.openflights_airports (
    openflights_id bigint primary key,
    name text not null,
    city text,
    country text,
    iata_code varchar(3),
    icao_code varchar(4),
    latitude double precision,
    longitude double precision,
    altitude_ft integer,
    utc_offset numeric,
    dst_code varchar(2),
    timezone text,
    location_type text,
    source text,
    updated_at timestamptz not null default now()
);

create index if not exists openflights_airports_iata_idx
    on public.openflights_airports (iata_code);
create index if not exists openflights_airports_icao_idx
    on public.openflights_airports (icao_code);
create index if not exists openflights_airports_city_idx
    on public.openflights_airports (city);
create index if not exists openflights_airports_country_idx
    on public.openflights_airports (country);

create table if not exists public.openflights_airlines (
    openflights_id bigint primary key,
    name text not null,
    alias text,
    iata_code varchar(3),
    icao_code varchar(4),
    callsign text,
    country text,
    active boolean not null default false,
    updated_at timestamptz not null default now()
);

create index if not exists openflights_airlines_iata_idx
    on public.openflights_airlines (iata_code);
create index if not exists openflights_airlines_icao_idx
    on public.openflights_airlines (icao_code);
create index if not exists openflights_airlines_country_idx
    on public.openflights_airlines (country);

create table if not exists public.openflights_routes (
    route_key varchar(40) primary key,
    airline_code varchar(3),
    airline_id bigint,
    source_airport_code varchar(4),
    source_airport_id bigint,
    destination_airport_code varchar(4),
    destination_airport_id bigint,
    codeshare boolean not null default false,
    stops integer not null default 0,
    equipment text,
    updated_at timestamptz not null default now()
);

create index if not exists openflights_routes_airline_idx
    on public.openflights_routes (airline_code);
create index if not exists openflights_routes_source_idx
    on public.openflights_routes (source_airport_code);
create index if not exists openflights_routes_destination_idx
    on public.openflights_routes (destination_airport_code);
