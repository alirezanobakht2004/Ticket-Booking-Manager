USE alibaba_db;

CREATE TABLE IF NOT EXISTS vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    capacity INT,
    reserved_number INT DEFAULT 0,
    brand VARCHAR(100),
    model VARCHAR(100)
);
