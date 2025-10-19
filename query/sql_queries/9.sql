/* 9_tehran_tickets_by_city.sql */
SELECT  loc.title        AS city,
        COUNT(*)         AS tickets_sold
FROM    ticket t
JOIN    location loc ON loc.location_id = t.destination
WHERE   loc.title LIKE '%Tehran%'
GROUP   BY loc.title
ORDER   BY tickets_sold DESC;
