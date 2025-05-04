USE alibaba_db;

CREATE TABLE IF NOT EXISTS ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT,
    vehicle_id INT,
    path TEXT,
    source INT,
    destination INT,
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    price FLOAT,
    id_number VARCHAR(100),
    class_code INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    seat_id INT,
    FOREIGN KEY (reservation_id) REFERENCES reservation(reservation_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id),
    FOREIGN KEY (source) REFERENCES location(location_id),
    FOREIGN KEY (destination) REFERENCES location(location_id),
    FOREIGN KEY (seat_id) REFERENCES seat(seat_id)
);
