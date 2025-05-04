USE alibaba_db;

CREATE TABLE IF NOT EXISTS train (
    vehicle_id INT PRIMARY KEY,
    train_type VARCHAR(50),
    wagon_count INT,
    star INT,
    bus_train BOOLEAN,
    food_service BOOLEAN,
    internet_connection BOOLEAN,
    closed_compartment BOOLEAN,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE
);
