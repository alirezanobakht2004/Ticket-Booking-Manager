USE alibaba_db;

CREATE TABLE IF NOT EXISTS passenger (
    person_id INT PRIMARY KEY,
    registered_trips TEXT,
    loyalty_point INT DEFAULT 0,
    passenger_type VARCHAR(50),
    FOREIGN KEY (person_id) REFERENCES person(person_id) ON DELETE CASCADE
);
