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
