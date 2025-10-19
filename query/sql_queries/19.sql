/* 19_delete_reddington_cancelled_tickets.sql */
DELETE t
FROM   ticket      t
JOIN   reservation r  ON r.reservation_id = t.reservation_id
JOIN   passenger   pa ON pa.person_id     = r.passenger_id
JOIN   person      p  ON p.person_id      = pa.person_id
WHERE  p.last_name = 'Reddington'
  AND  r.status    = 'CANCELLED';
