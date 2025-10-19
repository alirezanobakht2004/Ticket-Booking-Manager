DELIMITER //
CREATE PROCEDURE sp_cancelled_by_mode (IN p_type ENUM('bus','plane','train'))
BEGIN
  SELECT t.*, r.status
  FROM   ticket t
  JOIN   reservation r ON r.reservation_id = t.reservation_id
  JOIN   vehicle v ON v.vehicle_id = t.vehicle_id
       /* dynamic join to subtype */
  LEFT  JOIN bus   b  ON (p_type='bus'   AND b.vehicle_id  = v.vehicle_id)
  LEFT  JOIN plane pl ON (p_type='plane' AND pl.vehicle_id = v.vehicle_id)
  LEFT  JOIN train tr ON (p_type='train' AND tr.vehicle_id = v.vehicle_id)
  WHERE  r.status = 'CANCELLED'
    AND ((p_type='bus'   AND b.vehicle_id  IS NOT NULL) OR
         (p_type='plane' AND pl.vehicle_id IS NOT NULL) OR
         (p_type='train' AND tr.vehicle_id IS NOT NULL))
  ORDER BY t.created_at;
END //
DELIMITER ;
