USE alibaba_db;

CREATE TABLE IF NOT EXISTS bus (
    vehicle_id INT PRIMARY KEY,
    bus_type VARCHAR(50),
    bus_company VARCHAR(100),
    chair_decoration VARCHAR(50),
    air_condition BOOLEAN,
    internet_connection BOOLEAN,
    snack_service BOOLEAN,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE
);
