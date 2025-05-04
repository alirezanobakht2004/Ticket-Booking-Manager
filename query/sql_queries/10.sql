/* 10_cities_of_oldest_user.sql */
WITH oldest_user AS (
    SELECT person_id
    FROM   person
    ORDER  BY created_at    -- earliest registration
    LIMIT 1
)
SELECT DISTINCT loc.title AS city
FROM   oldest_user ou
JOIN   reservation r  ON r.passenger_id = ou.person_id
JOIN   ticket      t  ON t.reservation_id = r.reservation_id
JOIN   location    loc ON loc.location_id = t.destination
ORDER  BY loc.title;
