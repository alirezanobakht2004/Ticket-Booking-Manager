ALTER TABLE person     ADD INDEX idx_email_phone (email, phone_number);
ALTER TABLE ticket     ADD INDEX idx_ticket_created (created_at);
ALTER TABLE reservation ADD INDEX idx_res_status (status, passenger_id);
ALTER TABLE report     ADD INDEX idx_report_topic (report_type, person_id);

