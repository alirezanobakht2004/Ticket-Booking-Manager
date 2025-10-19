DELIMITER //
CREATE PROCEDURE sp_city_tickets (IN p_city VARCHAR(255))
BEGIN
  SELECT t.*
  FROM   ticket t
  JOIN   location loc ON loc.location_id = t.destination
  WHERE  loc.title = p_city
  ORDER  BY t.created_at;
END //
DELIMITER ;
