DELIMITER //
CREATE PROCEDURE sp_peers_same_city (IN p_id VARCHAR(100))
BEGIN
  DECLARE v_city VARCHAR(50);

  SELECT city INTO v_city
  FROM   person
  WHERE  email = p_id OR phone_number = p_id
  LIMIT  1;

  SELECT person_id, first_name, last_name, email, phone_number
  FROM   person
  WHERE  city = v_city
    AND  NOT (email = p_id OR phone_number = p_id);
END //
DELIMITER ;

