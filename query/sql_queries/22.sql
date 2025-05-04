/* 22_most_reported_ticket.sql */
SELECT  r.ticket_id,
        GROUP_CONCAT(DISTINCT r.report_type SEPARATOR ', ') AS subjects,
        COUNT(*)                                           AS report_count
FROM    report r
GROUP   BY r.ticket_id
ORDER   BY report_count DESC
LIMIT 1;
