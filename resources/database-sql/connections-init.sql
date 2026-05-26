BEGIN;

DROP TABLE IF EXISTS connections, login_attempts;

CREATE TABLE connections (
    id              INTEGER     GENERATED ALWAYS AS IDENTITY 
                                PRIMARY KEY,
    ip              INET        NOT NULL 
                                UNIQUE,
    blacklisted     BOOLEAN     DEFAULT FALSE
);

CREATE TABLE login_attempts (
    id              INTEGER     GENERATED ALWAYS AS IDENTITY 
                                PRIMARY KEY,
    connection_id   INTEGER     NOT NULL,
    failed_login    BOOLEAN     NOT NULL 
                                DEFAULT TRUE,
    time            TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE login_attempts 
ADD CONSTRAINT fk_con_login
FOREIGN KEY (connection_id) 
REFERENCES connections(id);

END;