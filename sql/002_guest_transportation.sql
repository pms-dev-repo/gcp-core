-- Guest Transportation operational source model.
--
-- The source exports contain guest PII and must be loaded separately.  This
-- migration intentionally contains schema and non-sensitive flight reference
-- data only.

create table if not exists public.odata_departures_all (
    id bigserial primary key,
    client_code text not null default 'GCPHOTEL',
    room_no integer,
    guest_name text,
    nights integer,
    arrival_date date,
    departure_date date,
    departure_group_date date,
    adults integer,
    children integer,
    rooms integer,
    room_type text,
    reservation_status text,
    departure_time text,
    payment_method text,
    rate_code text,
    vip text,
    share_with text,
    source_report text,
    source_file text,
    child_bucket_1 integer,
    child_bucket_2 integer,
    child_bucket_3 integer,
    imported_at timestamptz not null default now()
);

create table if not exists public.odata_arr_detail (
    id bigserial primary key,
    client_code text not null default 'GCPHOTEL',
    room_no integer,
    guest_name text,
    arrival_date date,
    departure_date date,
    room_type text,
    adults integer,
    children integer,
    rooms integer,
    market_code text,
    reservation_status text,
    arrival_group_date date,
    confirmation_no bigint,
    vip text,
    last_room text,
    carrier_code text,
    method_of_arrival text,
    prev_stays integer,
    prev_nights integer,
    share_with text,
    accompanying_names text,
    source_report text,
    source_file text,
    child_bucket_1 integer,
    child_bucket_2 integer,
    child_bucket_3 integer,
    arrival_time text,
    source_code text,
    observations text,
    visual_band_id text,
    visual_shade text,
    visual_page_number integer,
    visual_band_top numeric,
    visual_band_bottom numeric,
    imported_at timestamptz not null default now()
);

create table if not exists public.odata_transportation (
    id bigserial primary key,
    client_code text not null default 'GCPHOTEL',
    transport_direction text,
    transport_type text,
    guest_name text,
    transport_datetime timestamp without time zone,
    transport_date date,
    stay_date date,
    station_code text,
    carrier_code text,
    transport_code text,
    adults integer,
    children integer,
    room_no integer,
    vip text,
    reservation_status text,
    source_report text,
    source_file text,
    loaded_at timestamp without time zone default now(),
    transport_time time without time zone,
    constraint odata_transportation_direction_check
        check (
            transport_direction is null
            or upper(transport_direction) in ('PICKUP', 'DROPOFF', 'TRANSFER')
        )
);

create table if not exists public.snapshot (
    id bigserial primary key,
    client_code text not null default 'GCPHOTEL',
    confirmation_number integer,
    reservation_status text,
    stay_date date,
    adults integer,
    children integer,
    child_bucket_1 integer,
    child_bucket_2 integer,
    child_bucket_3 integer,
    source_report text,
    source_file text,
    loaded_at timestamp without time zone default now(),
    room_type text,
    room_no integer,
    children_ages text,
    source_code text,
    rate_code text,
    anniversary_date date,
    first_name text,
    last_name text,
    vip_code text
);

-- This is deliberately joined to OpenFlights by code rather than by foreign
-- key.  The OpenFlights import is an external reference catalog and may be
-- refreshed independently.
create table if not exists public.flight_reference (
    id bigserial primary key,
    flight_number varchar(10) unique,
    airline_code varchar(5),
    origin_iata varchar(3),
    destination_iata varchar(3),
    active boolean default true,
    created_at timestamp without time zone default now()
);

create table if not exists public.guest_transportation_assignments (
    record_key text primary key,
    client_code text not null,
    direction text not null
        check (direction in ('Arrival', 'Departure')),
    movement_date date not null,
    guest_name text not null,
    status text not null default 'Pending',
    transfer_type text,
    pickup_time text,
    flight text,
    pickup_location text,
    destination text,
    vehicle_type text,
    vehicle text,
    driver text,
    driver_phone text,
    notes text,
    updated_at timestamptz not null default now()
);

create index if not exists odata_departures_client_date_idx
    on public.odata_departures_all (client_code, departure_date);
create index if not exists odata_departures_client_guest_idx
    on public.odata_departures_all (client_code, upper(btrim(guest_name)));
create index if not exists odata_departures_client_room_idx
    on public.odata_departures_all (client_code, room_no);

create index if not exists odata_arrivals_client_date_idx
    on public.odata_arr_detail (client_code, arrival_date);
create index if not exists odata_arrivals_client_guest_idx
    on public.odata_arr_detail (client_code, upper(btrim(guest_name)));
create index if not exists odata_arrivals_client_confirmation_idx
    on public.odata_arr_detail (client_code, confirmation_no);
create index if not exists odata_arrivals_client_room_idx
    on public.odata_arr_detail (client_code, room_no);

create index if not exists odata_transportation_pickup_idx
    on public.odata_transportation (
        client_code,
        transport_direction,
        stay_date,
        transport_datetime
    );
create index if not exists odata_transportation_dropoff_idx
    on public.odata_transportation (
        client_code,
        transport_direction,
        transport_date,
        transport_datetime
    );
create index if not exists odata_transportation_guest_idx
    on public.odata_transportation (client_code, upper(btrim(guest_name)));
create index if not exists odata_transportation_room_idx
    on public.odata_transportation (client_code, room_no);

create index if not exists snapshot_client_stay_idx
    on public.snapshot (client_code, stay_date);
create index if not exists snapshot_client_room_idx
    on public.snapshot (client_code, room_no);
create index if not exists snapshot_client_rate_idx
    on public.snapshot (client_code, rate_code);

create index if not exists flight_reference_airline_idx
    on public.flight_reference (airline_code);
create index if not exists flight_reference_origin_idx
    on public.flight_reference (origin_iata);
create index if not exists flight_reference_destination_idx
    on public.flight_reference (destination_iata);
create index if not exists guest_transportation_assignments_client_date_idx
    on public.guest_transportation_assignments (client_code, movement_date);

insert into public.flight_reference (
    flight_number,
    airline_code,
    origin_iata,
    destination_iata,
    active
)
values
    ('AA585', 'AA', 'MIA', 'BGI', true),
    ('AC1840', 'AC', 'YYZ', 'BGI', true),
    ('B60361', 'B6', 'BOS', 'BGI', true),
    ('B62661', 'B6', 'JFK', 'BGI', true),
    ('BA255', 'BA', 'LHR', 'BGI', true),
    ('DL1985', 'DL', 'ATL', 'BGI', true)
on conflict (flight_number) do update set
    airline_code = excluded.airline_code,
    origin_iata = excluded.origin_iata,
    destination_iata = excluded.destination_iata,
    active = excluded.active;

create or replace view public.vw_business_date
with (security_invoker = true)
as
select (now() at time zone 'America/Barbados')::date as business_date;

create or replace view public.vw_daily_arrivals_transportation
with (security_invoker = true)
as
with business_day as (
    select (now() at time zone 'America/Barbados')::date as business_date
)
select
    a.client_code,
    a.room_no,
    a.guest_name,
    a.arrival_date,
    a.departure_date,
    a.room_type,
    a.adults,
    a.children,
    a.rooms,
    a.market_code,
    a.reservation_status,
    a.confirmation_no,
    a.vip,
    a.prev_stays,
    a.prev_nights,
    a.last_room,
    a.carrier_code as arrival_carrier_code,
    a.method_of_arrival,
    t.transport_direction,
    t.transport_type,
    t.transport_datetime,
    t.transport_date,
    t.stay_date as transport_stay_date,
    t.station_code,
    t.carrier_code as transport_flight,
    t.transport_code,
    t.room_no as transport_room_no,
    t.vip as transport_vip,
    t.reservation_status as transport_reservation_status,
    fr.airline_code,
    airline.name as airline_name,
    fr.origin_iata,
    origin_airport.name as origin_airport,
    origin_airport.city as origin_city,
    origin_airport.country as origin_country,
    fr.destination_iata,
    destination_airport.name as destination_airport,
    destination_airport.city as destination_city,
    destination_airport.country as destination_country,
    a.share_with,
    a.accompanying_names,
    a.arrival_time,
    a.source_code,
    to_char(t.transport_time::interval, 'HH24:MI') as transport_time,
    to_char(t.transport_time::interval + interval '1 hour', 'HH24:MI') as exp_arr_hotel,
    coalesce(a.adults, 0) + coalesce(a.children, 0) as passengers,
    greatest(a.departure_date - a.arrival_date, 0) as number_of_nights
from public.odata_arr_detail a
cross join business_day bd
left join lateral (
    select tr.*
    from public.odata_transportation tr
    where tr.client_code = a.client_code
      and upper(tr.transport_direction) = 'PICKUP'
      and tr.stay_date = a.arrival_date
      and (
          upper(btrim(tr.guest_name)) = upper(btrim(a.guest_name))
          or nullif(btrim(tr.room_no::text), '') = nullif(btrim(a.room_no::text), '')
      )
    order by
        case
            when upper(btrim(tr.guest_name)) = upper(btrim(a.guest_name)) then 0
            else 1
        end,
        tr.transport_datetime
    limit 1
) t on true
left join public.flight_reference fr
    on regexp_replace(
           upper(replace(btrim(regexp_replace(coalesce(t.carrier_code, ''), '^.*/', '')), ' ', '')),
           '^([A-Z]{2,3})0+([0-9])',
           '\1\2'
       ) = regexp_replace(
           upper(replace(btrim(coalesce(fr.flight_number, '')), ' ', '')),
           '^([A-Z]{2,3})0+([0-9])',
           '\1\2'
       )
   and fr.active is true
left join lateral (
    select oa.name
    from public.openflights_airlines oa
    where oa.iata_code = fr.airline_code
      and oa.active is true
    order by oa.openflights_id
    limit 1
) airline on true
left join lateral (
    select ap.name, ap.city, ap.country
    from public.openflights_airports ap
    where ap.iata_code = fr.origin_iata
    order by ap.openflights_id
    limit 1
) origin_airport on true
left join lateral (
    select ap.name, ap.city, ap.country
    from public.openflights_airports ap
    where ap.iata_code = fr.destination_iata
    order by ap.openflights_id
    limit 1
) destination_airport on true
where a.arrival_date = bd.business_date
order by t.transport_datetime, a.room_no;

create or replace view public.vw_daily_departures_transportation
with (security_invoker = true)
as
with business_day as (
    select (now() at time zone 'America/Barbados')::date as business_date
)
select
    d.client_code,
    d.room_no,
    d.guest_name,
    d.arrival_date,
    d.departure_date,
    d.nights,
    d.adults,
    d.children,
    d.rooms,
    d.room_type,
    d.reservation_status,
    d.departure_time,
    d.payment_method,
    d.rate_code,
    d.vip,
    t.transport_direction,
    t.transport_type,
    t.transport_datetime,
    t.transport_date,
    t.station_code,
    case
        when upper(regexp_replace(btrim(t.carrier_code), '\s+', '', 'g'))
             ~ '^[A-Z0-9]{2}[0-9]+$'
        then left(upper(regexp_replace(btrim(t.carrier_code), '\s+', '', 'g')), 2)
             || substring(
                    upper(regexp_replace(btrim(t.carrier_code), '\s+', '', 'g'))
                    from 3
                )::integer::text
        else upper(regexp_replace(btrim(t.carrier_code), '\s+', '', 'g'))
    end as transport_flight,
    t.transport_code,
    fr.airline_code,
    airline.name as airline_name,
    fr.origin_iata,
    origin_airport.city as origin_city,
    origin_airport.country as origin_country,
    fr.destination_iata,
    destination_airport.city as destination_city,
    destination_airport.country as destination_country,
    to_char(t.transport_time::interval, 'HH24:MI') as transport_time,
    coalesce(d.adults, 0) + coalesce(d.children, 0) as passengers,
    origin_airport.name as origin_airport,
    destination_airport.name as destination_airport
from public.odata_departures_all d
cross join business_day bd
join public.odata_transportation t
    on t.client_code = d.client_code
   and upper(btrim(t.guest_name)) = upper(btrim(d.guest_name))
   and upper(t.transport_direction) = 'DROPOFF'
   and t.transport_date = d.departure_date
left join public.flight_reference fr
    on upper(replace(btrim(regexp_replace(t.carrier_code, '^.*[/]', '')), ' ', ''))
       = upper(replace(btrim(fr.flight_number), ' ', ''))
   and fr.active is true
left join lateral (
    select oa.name
    from public.openflights_airlines oa
    where oa.iata_code = fr.airline_code
      and oa.active is true
    order by oa.openflights_id
    limit 1
) airline on true
left join lateral (
    select ap.name, ap.city, ap.country
    from public.openflights_airports ap
    where ap.iata_code = fr.origin_iata
    order by ap.openflights_id
    limit 1
) origin_airport on true
left join lateral (
    select ap.name, ap.city, ap.country
    from public.openflights_airports ap
    where ap.iata_code = fr.destination_iata
    order by ap.openflights_id
    limit 1
) destination_airport on true
where d.departure_date = bd.business_date
order by t.transport_datetime, d.room_no;

create or replace view public.vw_daily_figures
with (security_invoker = true)
as
with business_day as (
    select (now() at time zone 'America/Barbados')::date as business_date
), clients as (
    select client_code from public.snapshot
    union
    select client_code from public.odata_arr_detail
    union
    select client_code from public.odata_departures_all
), figures as (
    select
        c.client_code,
        1 as sort_order,
        'Adults'::text as metric,
        (select coalesce(sum(s.adults), 0) from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date) as in_house,
        (select coalesce(sum(d.adults), 0) from public.odata_departures_all d, business_day bd
         where d.client_code = c.client_code and d.departure_date = bd.business_date) as less_departure,
        (select coalesce(sum(a.adults), 0) from public.odata_arr_detail a, business_day bd
         where a.client_code = c.client_code and a.arrival_date = bd.business_date) as plus_arrivals,
        (select coalesce(sum(s.adults), 0) from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date
           and upper(btrim(s.rate_code)) in ('COMP', 'HOUSE')) as exo
    from clients c
    union all
    select
        c.client_code,
        bucket.sort_order,
        bucket.metric,
        (select coalesce(sum(
            case bucket.sort_order
                when 2 then s.child_bucket_3
                when 3 then s.child_bucket_2
                else s.child_bucket_1
            end
        ), 0) from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date),
        (select coalesce(sum(
            case bucket.sort_order
                when 2 then d.child_bucket_3
                when 3 then d.child_bucket_2
                else d.child_bucket_1
            end
        ), 0) from public.odata_departures_all d, business_day bd
         where d.client_code = c.client_code and d.departure_date = bd.business_date),
        (select coalesce(sum(
            case bucket.sort_order
                when 2 then a.child_bucket_3
                when 3 then a.child_bucket_2
                else a.child_bucket_1
            end
        ), 0) from public.odata_arr_detail a, business_day bd
         where a.client_code = c.client_code and a.arrival_date = bd.business_date),
        null::bigint
    from clients c
    cross join (
        values
            (2, 'Children -18'::text),
            (3, 'Children -12'::text),
            (4, 'Children -3'::text)
    ) bucket(sort_order, metric)
    union all
    select
        c.client_code,
        5,
        'Persons'::text,
        (select coalesce(sum(s.adults), 0) + coalesce(sum(s.children), 0)
         from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date),
        (select coalesce(sum(d.adults), 0) + coalesce(sum(d.children), 0)
         from public.odata_departures_all d, business_day bd
         where d.client_code = c.client_code and d.departure_date = bd.business_date),
        (select coalesce(sum(a.adults), 0) + coalesce(sum(a.children), 0)
         from public.odata_arr_detail a, business_day bd
         where a.client_code = c.client_code and a.arrival_date = bd.business_date),
        (select coalesce(sum(s.adults), 0) + coalesce(sum(s.children), 0)
         from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date
           and upper(btrim(s.rate_code)) in ('COMP', 'HOUSE'))
    from clients c
    union all
    select
        c.client_code,
        6,
        'Rooms'::text,
        (select count(distinct s.room_no) from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date),
        (select coalesce(sum(d.rooms), 0) from public.odata_departures_all d, business_day bd
         where d.client_code = c.client_code and d.departure_date = bd.business_date),
        (select coalesce(sum(a.rooms), 0) from public.odata_arr_detail a, business_day bd
         where a.client_code = c.client_code and a.arrival_date = bd.business_date),
        (select count(distinct s.room_no) from public.snapshot s, business_day bd
         where s.client_code = c.client_code and s.stay_date = bd.business_date
           and upper(btrim(s.rate_code)) in ('COMP', 'HOUSE'))
    from clients c
)
select
    bd.business_date,
    f.client_code,
    f.sort_order,
    f.metric,
    f.in_house,
    f.less_departure,
    f.plus_arrivals,
    f.in_house - f.less_departure + f.plus_arrivals as exp_in_house,
    f.exo
from figures f
cross join business_day bd
order by f.client_code, f.sort_order;

alter table public.odata_departures_all enable row level security;
alter table public.odata_arr_detail enable row level security;
alter table public.odata_transportation enable row level security;
alter table public.snapshot enable row level security;
alter table public.flight_reference enable row level security;
alter table public.guest_transportation_assignments enable row level security;

revoke all on table public.odata_departures_all from anon, authenticated;
revoke all on table public.odata_arr_detail from anon, authenticated;
revoke all on table public.odata_transportation from anon, authenticated;
revoke all on table public.snapshot from anon, authenticated;
revoke all on table public.flight_reference from anon, authenticated;
revoke all on table public.guest_transportation_assignments from anon, authenticated;
revoke all on table public.vw_business_date from anon, authenticated;
revoke all on table public.vw_daily_arrivals_transportation from anon, authenticated;
revoke all on table public.vw_daily_departures_transportation from anon, authenticated;
revoke all on table public.vw_daily_figures from anon, authenticated;

grant select, insert, update, delete on table public.odata_departures_all to service_role;
grant select, insert, update, delete on table public.odata_arr_detail to service_role;
grant select, insert, update, delete on table public.odata_transportation to service_role;
grant select, insert, update, delete on table public.snapshot to service_role;
grant select, insert, update, delete on table public.flight_reference to service_role;
grant select, insert, update, delete on table public.guest_transportation_assignments to service_role;
grant usage, select on all sequences in schema public to service_role;
grant select on table public.vw_business_date to service_role;
grant select on table public.vw_daily_arrivals_transportation to service_role;
grant select on table public.vw_daily_departures_transportation to service_role;
grant select on table public.vw_daily_figures to service_role;
