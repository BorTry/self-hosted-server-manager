BEGIN;

DROP SCHEMA IF EXISTS admin CASCADE;
CREATE SCHEMA IF NOT EXISTS admin;

CREATE TABLE admin.connections (
    id              INTEGER     GENERATED ALWAYS AS IDENTITY 
                                PRIMARY KEY,
    ip              INET        NOT NULL 
                                UNIQUE,
    blacklisted     BOOLEAN     DEFAULT FALSE
);

CREATE TABLE admin.login_attempts (
    id              INTEGER     GENERATED ALWAYS AS IDENTITY 
                                PRIMARY KEY,
    connection_id   INTEGER     NOT NULL,
    failed_login    BOOLEAN     NOT NULL 
                                DEFAULT TRUE,
    time            TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE admin.login_attempts 
ADD CONSTRAINT fk_con_login
FOREIGN KEY (connection_id) 
REFERENCES admin.connections(id);

END;