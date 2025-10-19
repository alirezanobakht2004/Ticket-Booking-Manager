/* 7_tickets_by_mode.sql */
SELECT
    CASE
      WHEN b.vehicle_id  IS NOT NULL THEN 'bus'
      WHEN pl.vehicle_id IS NOT NULL THEN 'plane'
      WHEN tr.vehicle_id IS NOT NULL THEN 'train'
      ELSE 'unknown'
    END AS transport_type,
    COUNT(*) AS tickets_sold
FROM   ticket t
LEFT  JOIN bus   b  ON b.vehicle_id  = t.vehicle_id
LEFT  JOIN plane pl ON pl.vehicle_id = t.vehicle_id
LEFT  JOIN train tr ON tr.vehicle_id = t.vehicle_id
GROUP BY transport_type;
