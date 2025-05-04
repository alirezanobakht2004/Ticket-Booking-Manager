USE alibaba_db;

CREATE TABLE IF NOT EXISTS report (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    reservation_id INT,
    ticket_id INT,
    payment_id INT,
    report_type VARCHAR(100),
    report_text TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(person_id),
    FOREIGN KEY (reservation_id) REFERENCES reservation(reservation_id),
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id)
);



ALTER TABLE ticket
  MODIFY departure_time DATETIME          NOT NULL,
  MODIFY arrival_time   DATETIME          NOT NULL;


-- ─── Phase‑2 & 3 heavy paths ───────────────────────────────────
ALTER TABLE ticket
  ADD INDEX idx_res (reservation_id),                 -- Q6‑14 look‑ups
  ADD INDEX idx_created (created_at),                 -- Q8, Q15, Q21
  ADD INDEX idx_dst (destination),                    -- Q4, Q9
  ADD INDEX idx_src_dst_time (source,destination,departure_time); -- Phase‑3 searches

ALTER TABLE reservation
  ADD INDEX idx_passenger_status (passenger_id,status);  -- Q17 & deletes

ALTER TABLE payment
  ADD INDEX idx_res_paytime (reservation_id,payment_time); -- Q3, future monthly sales

ALTER TABLE report
  ADD INDEX idx_ticket (ticket_id);                     -- Q22
ALTER TABLE plane
  ADD INDEX idx_airline (airline_name);                 -- Q21
