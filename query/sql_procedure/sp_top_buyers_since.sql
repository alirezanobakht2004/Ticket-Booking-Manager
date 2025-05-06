DELIMITER //
CREATE PROCEDURE sp_top_buyers_since (IN p_date DATETIME, IN p_n INT)
BEGIN
  SELECT  pe.person_id, pe.first_name, pe.last_name,
          COUNT(*) AS tickets_since
  FROM    ticket      t
  JOIN    reservation r  ON r.reservation_id = t.reservation_id
  JOIN    person     pe  ON pe.person_id      = r.passenger_id
  WHERE   t.created_at >= p_date
  GROUP   BY pe.person_id
  ORDER   BY tickets_since DESC
  LIMIT   p_n;
END //
DELIMITER ;
