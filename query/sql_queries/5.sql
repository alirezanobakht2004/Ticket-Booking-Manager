/* ---------- 5_most_recent_ticket_buyer.sql ---------- */
SELECT  p.*
FROM    ticket      t
JOIN    reservation r  ON r.reservation_id = t.reservation_id
JOIN    passenger  pa  ON pa.person_id     = r.passenger_id
JOIN    person     p   ON p.person_id      = pa.person_id
ORDER BY t.departure_time DESC          -- or t.created_at if you track it
LIMIT   1;                              -- remove LIMIT to show all ties
