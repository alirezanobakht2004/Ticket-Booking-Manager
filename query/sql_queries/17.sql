WITH cancels AS (
    SELECT rep.person_id, COUNT(*) AS cnt
    FROM   report rep FORCE INDEX (idx_ticket)        -- use the new index
    WHERE  rep.status='CANCELLED'
    GROUP  BY rep.person_id
), totals AS (
    SELECT SUM(cnt) AS grand_cnt FROM cancels
)
SELECT  p.first_name, p.last_name,
        ROUND(c.cnt / totals.grand_cnt * 100,2) AS cancel_pct
FROM    cancels c
JOIN    totals
JOIN    person  p ON p.person_id = c.person_id
ORDER   BY c.cnt DESC
LIMIT 1;

