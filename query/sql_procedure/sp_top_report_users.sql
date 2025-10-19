DELIMITER //
CREATE PROCEDURE sp_top_report_users (IN p_topic VARCHAR(100))
BEGIN
  WITH ranked AS (
      SELECT r.person_id,
             COUNT(*) AS rpt_cnt,
             DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rk
      FROM   report r
      WHERE  r.report_type = p_topic
      GROUP  BY r.person_id
  )
  SELECT p.person_id, p.first_name, p.last_name, r.rpt_cnt
  FROM   ranked r
  JOIN   person p ON p.person_id = r.person_id
  WHERE  r.rk = 1;          -- all co‑leaders if tie
END //
DELIMITER ;
