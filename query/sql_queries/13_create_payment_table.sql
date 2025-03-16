USE alibaba_db;

CREATE TABLE IF NOT EXISTS payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT,
    payment_method VARCHAR(50),
    amount VARCHAR(50),
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    transaction_reference VARCHAR(100),
    FOREIGN KEY (reservation_id) REFERENCES reservation(reservation_id)
);
