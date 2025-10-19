DELIMITER //
CREATE PROCEDURE sp_support_cancelled_users (IN p_id VARCHAR(100))
BEGIN
  SELECT DISTINCT pu.person_id, pu.first_name, pu.last_name
  FROM   person sup                           -- support person
  JOIN   report rep ON rep.person_id = sup.person_id
  JOIN   reservation r ON r.reservation_id = rep.reservation_id
  JOIN   person pu  ON pu.person_id = r.passenger_id
  WHERE  (sup.email       = p_id OR sup.phone_number = p_id)
    AND  r.status = 'CANCELLED';
END //
DELIMITER ;

