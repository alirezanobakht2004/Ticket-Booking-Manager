/* 12_min_two_tickets.sql */
WITH cnt AS (
    SELECT r.passenger_id AS person_id, COUNT(*) AS ticket_cnt
    FROM   ticket t
    JOIN   reservation r ON r.reservation_id = t.reservation_id
    GROUP  BY r.passenger_id
    HAVING ticket_cnt >= 2
)
SELECT  p.person_id, p.first_name, p.last_name, cnt.ticket_cnt
FROM    cnt
JOIN    person p ON p.person_id = cnt.person_id
ORDER   BY cnt.ticket_cnt DESC;
