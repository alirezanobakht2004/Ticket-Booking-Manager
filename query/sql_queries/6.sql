WITH user_totals AS (
    SELECT r.passenger_id,
           SUM(pay.amount+0.0) AS tot               /* +0.0 avoids CAST() */
    FROM   payment pay
    JOIN   reservation r ON r.reservation_id = pay.reservation_id
    GROUP  BY r.passenger_id
),
avg_val AS ( SELECT AVG(tot) AS avg_tot FROM user_totals )
SELECT  p.email, p.phone_number, ut.tot
FROM    user_totals ut
JOIN    avg_val a
JOIN    person p ON p.person_id = ut.passenger_id
WHERE   ut.tot  > a.avg_tot
ORDER  BY ut.tot DESC;

