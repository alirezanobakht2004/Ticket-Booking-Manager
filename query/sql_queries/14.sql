/* 14_users_all_modes.sql */
WITH user_modes AS (
    SELECT r.passenger_id AS person_id,
           MAX(b.vehicle_id  IS NOT NULL) AS bus_flag,
           MAX(pl.vehicle_id IS NOT NULL) AS plane_flag,
           MAX(tr.vehicle_id IS NOT NULL) AS train_flag
    FROM   ticket t
    JOIN   reservation r ON r.reservation_id = t.reservation_id
    LEFT  JOIN bus   b  ON b.vehicle_id  = t.vehicle_id
    LEFT  JOIN plane pl ON pl.vehicle_id = t.vehicle_id
    LEFT  JOIN train tr ON tr.vehicle_id = t.vehicle_id
    GROUP  BY r.passenger_id
)
SELECT  p.person_id, p.first_name, p.last_name,
        p.email, p.phone_number
FROM    user_modes um
JOIN    person p ON p.person_id = um.person_id
WHERE   um.bus_flag   = 1
  AND   um.plane_flag = 1
  AND   um.train_flag = 1
ORDER   BY p.person_id;
