USE alibaba_db;

CREATE TABLE IF NOT EXISTS seat (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_number VARCHAR(50),
    seat_number VARCHAR(50)
);
