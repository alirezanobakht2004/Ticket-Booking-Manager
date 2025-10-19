/* ---------- 4_one_ticket_per_city.sql ---------- */
WITH per_city AS (                 -- ticket count per (user, city)
    SELECT r.passenger_id  AS person_id,
           t.destination   AS city_id,
           COUNT(*)        AS cnt
    FROM   reservation r
    JOIN   ticket      t ON t.reservation_id = r.reservation_id
    GROUP  BY r.passenger_id, t.destination
),
qual_users AS (                    -- keep users whose MAX(cnt)=1
    SELECT person_id
    FROM   per_city
    GROUP  BY person_id
    HAVING MAX(cnt) = 1            -- never more than one ticket per city
)
SELECT p.person_id,
       p.first_name,
       p.last_name
FROM   person p
JOIN   qual_users q ON q.person_id = p.person_id
ORDER  BY p.person_id;
