USE alibaba_db;

CREATE TABLE IF NOT EXISTS support (
    person_id INT PRIMARY KEY,
    work_position VARCHAR(100),
    staff_number VARCHAR(50),
    department VARCHAR(100),
    FOREIGN KEY (person_id) REFERENCES person(person_id) ON DELETE CASCADE
);
