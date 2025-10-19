/* 20_delete_all_cancelled_tickets.sql */
DELETE t
FROM   ticket      t
JOIN   reservation r ON r.reservation_id = t.reservation_id
WHERE  r.status = 'CANCELLED';
