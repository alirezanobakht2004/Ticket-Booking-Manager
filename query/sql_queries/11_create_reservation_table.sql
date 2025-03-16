USE alibaba_db;

CREATE TABLE IF NOT EXISTS reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    passenger_id INT,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    expiry_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (passenger_id) REFERENCES passenger(person_id) ON DELETE CASCADE
);
