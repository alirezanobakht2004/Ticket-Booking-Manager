/* 21_discount_mahan_yesterday.sql */
UPDATE ticket      t
JOIN   plane       pl ON pl.vehicle_id = t.vehicle_id
SET    t.price = t.price * 0.90
WHERE  pl.airline_name  = 'Mahan Air'
  AND  DATE(t.created_at) = CURDATE() - INTERVAL 1 DAY;   -- use t.departure_time if that’s your “sale date”
