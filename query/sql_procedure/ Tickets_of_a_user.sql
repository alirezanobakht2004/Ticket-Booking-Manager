DELIMITER //
CREATE PROCEDURE sp_user_tickets (IN p_id VARCHAR(100))
BEGIN
  SELECT t.*
  FROM   person p
  JOIN   reservation r ON r.passenger_id = p.person_id
  JOIN   ticket      t ON t.reservation_id = r.reservation_id
  WHERE  p.email = p_id OR p.phone_number = p_id
  ORDER  BY t.created_at;           -- change to departure_time if preferred
END //
DELIMITER ;
