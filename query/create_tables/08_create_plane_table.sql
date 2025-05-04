USE alibaba_db;

CREATE TABLE IF NOT EXISTS plane (
    vehicle_id INT PRIMARY KEY,
    airline_name VARCHAR(100),
    plane_type VARCHAR(100),
    stops_number INT,
    flight_number VARCHAR(100),
    destination_airport VARCHAR(100),
    departure_airport VARCHAR(100),
    internet_connection BOOLEAN,
    closed_compartment BOOLEAN,
    bed_chair BOOLEAN,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE
);
