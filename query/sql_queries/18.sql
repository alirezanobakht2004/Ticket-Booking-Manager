/* 18_update_top_canceller.sql */
UPDATE person
SET    last_name = 'Reddington'
WHERE  person_id = (
    SELECT person_id                       -- passenger with most cancellations
    FROM (
        SELECT r.passenger_id  AS person_id,
               COUNT(*)        AS cancel_cnt
        FROM   reservation r
        WHERE  r.status = 'CANCELLED'      -- ← your cancellation flag
        GROUP  BY r.passenger_id
        ORDER  BY cancel_cnt DESC
        LIMIT 1
    ) AS x
);
