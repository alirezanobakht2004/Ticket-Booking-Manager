DELIMITER //
CREATE PROCEDURE sp_search_phrase (IN p_phrase VARCHAR(100))
BEGIN
  SELECT t.*, CONCAT(pe.first_name,' ',pe.last_name) AS passenger_name
  FROM   ticket      t
  JOIN   reservation r  ON r.reservation_id = t.reservation_id
  JOIN   person     pe  ON pe.person_id      = r.passenger_id
  WHERE  CONCAT_WS(' ', pe.first_name, pe.last_name,
                   t.path, t.class_code)  LIKE CONCAT('%',p_phrase,'%');
END //
DELIMITER ;
