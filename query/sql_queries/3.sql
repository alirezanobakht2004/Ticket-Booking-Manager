/* ---------- 3_payments_by_month.sql ---------- */
SELECT  p.person_id,
        p.first_name,
        p.last_name,
        DATE_FORMAT(pay.payment_time, '%Y‑%m')          AS pay_month,   -- e.g. 2025‑04
        SUM(CAST(pay.amount AS DECIMAL(10,2)))          AS total_paid
FROM    person        AS p
JOIN    reservation   AS r    ON r.passenger_id   = p.person_id
JOIN    payment       AS pay  ON pay.reservation_id = r.reservation_id
GROUP BY p.person_id, pay_month
ORDER BY p.person_id, pay_month;
