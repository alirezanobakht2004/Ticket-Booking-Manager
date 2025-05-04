/* 15_today_tickets.sql */
SELECT *
FROM   ticket
WHERE  DATE(created_at) = CURDATE()
ORDER  BY created_at;
