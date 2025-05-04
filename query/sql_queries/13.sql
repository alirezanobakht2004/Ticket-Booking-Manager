/* 13_max_two_train_tickets.sql */
WITH train_cnt AS (
    SELECT r.passenger_id AS person_id, COUNT(*) AS train_tickets
    FROM   ticket t
    JOIN   train  tr ON tr.vehicle_id = t.vehicle_id    -- ↔ bus/plane for other modes
    JOIN   reservation r ON r.reservation_id = t.reservation_id
    GROUP  BY r.passenger_id
    HAVING train_tickets <= 2
)
SELECT  p.person_id, p.first_name, p.last_name, train_tickets
FROM    train_cnt
JOIN    person p ON p.person_id = train_cnt.person_id
ORDER   BY train_tickets;
