/* 11_cytra_sponsors.sql */
SELECT DISTINCT bus_company AS sponsor
FROM   bus
WHERE  bus_company LIKE '%Cytra%'
UNION
SELECT DISTINCT airline_name
FROM   plane
WHERE  airline_name LIKE '%Cytra%';
