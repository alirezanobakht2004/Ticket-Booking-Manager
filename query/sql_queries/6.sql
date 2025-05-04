/* 6_top_payers.sql */
WITH user_totals AS (
    SELECT r.passenger_id     AS person_id,
           SUM(CAST(pay.amount AS DECIMAL(10,2))) AS total_paid
    FROM   reservation r
    JOIN   payment pay ON pay.reservation_id = r.reservation_id
    GROUP  BY r.passenger_id
),
avg_total AS (
    SELECT AVG(total_paid) AS avg_tot FROM user_totals
)
SELECT  p.person_id, p.first_name, p.last_name,
        p.email, p.phone_number, u.total_paid
FROM    user_totals u
JOIN    avg_total a
JOIN    person p ON p.person_id = u.person_id
WHERE   u.total_paid > a.avg_tot
ORDER BY u.total_paid DESC;
