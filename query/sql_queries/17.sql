/* 17_top_cancellation_supporter.sql */
WITH cancels AS (
    SELECT rep.person_id                    AS support_id,
           COUNT(*)                         AS cancel_cnt
    FROM   report rep
    WHERE  rep.status = 'CANCELLED'
    GROUP  BY rep.person_id
),
tot AS ( SELECT SUM(cancel_cnt) AS total_cancel FROM cancels ),
leader AS (
    SELECT support_id, cancel_cnt
    FROM   cancels
    ORDER  BY cancel_cnt DESC
    LIMIT 1
)
SELECT  p.person_id,
        p.first_name,
        p.last_name,
        s.work_position,
        l.cancel_cnt,
        ROUND(l.cancel_cnt / tot.total_cancel * 100, 2) AS cancel_pct
FROM    leader l
JOIN    tot
JOIN    person  p ON p.person_id = l.support_id
JOIN    support s ON s.person_id = l.support_id;
