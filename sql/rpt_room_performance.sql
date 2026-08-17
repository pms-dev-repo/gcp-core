create or replace view public.rpt_room_performance as
select
  property,
  room_number,
  room_type,
  sum(room_nights)::integer as room_nights,
  count(*)::integer as stay_count
from public.rpt_guest_stay_classification
where room_number is not null
  and trim(room_number) <> ''
group by property, room_number, room_type;
