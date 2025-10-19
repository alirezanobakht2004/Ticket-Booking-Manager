/* 16_second_best_selling_class.sql */
SELECT class_code, ticket_count
FROM (
    SELECT class_code, COUNT(*) AS ticket_count,
           DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
    FROM   ticket
    GROUP  BY class_code
) ranked
WHERE rnk = 2;
