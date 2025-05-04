/* 8_top3_last_week.sql */
WITH last_week AS (
    SELECT r.passenger_id     AS person_id,
           COUNT(*)           AS week_tickets
    FROM   ticket t
    JOIN   reservation r ON r.reservation_id = t.reservation_id
    WHERE  t.created_at >= CURDATE() - INTERVAL 7 DAY   -- use t.departure_time if preferred
    GROUP  BY r.passenger_id
)
SELECT  p.person_id, p.first_name, p.last_name, lw.week_tickets
FROM    last_week lw
JOIN    person p ON p.person_id = lw.person_id
ORDER BY lw.week_tickets DESC
LIMIT 3;
