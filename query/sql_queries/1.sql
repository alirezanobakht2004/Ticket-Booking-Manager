/* ---------- 1_no_ticket_users.sql ---------- */
SELECT  p.person_id,
        p.first_name,
        p.last_name
FROM    person AS p
WHERE  NOT EXISTS (          -- no ticket rows reachable through this person
          SELECT 1
          FROM   reservation r
          JOIN   ticket      t  ON t.reservation_id = r.reservation_id
          WHERE  r.passenger_id = p.person_id
);

