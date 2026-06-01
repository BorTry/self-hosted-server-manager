BEGIN;

DROP SCHEMA IF EXISTS servers CASCADE;
CREATE SCHEMA IF NOT EXISTS servers;

DROP TABLE IF EXISTS servers.container, servers.ports_mapping, servers.ports;

CREATE TABLE servers.container (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY
                                    PRIMARY KEY,
    name            VARCHAR(127)    NOT NULL
                                    UNIQUE
);

CREATE TABLE servers.ports_mapping (
    id              INTEGER     GENERATED ALWAYS AS IDENTITY
                                PRIMARY KEY,
    server_id       INTEGER     NOT NULL,
    ports_open      BOOLEAN     NOT NULL
                                DEFAULT FALSE
);

ALTER TABLE servers.ports_mapping
ADD CONSTRAINT fk_mapping_container
FOREIGN KEY (server_id)
REFERENCES servers.container(id);

CREATE TABLE servers.ports (
    id              INTEGER     GENERATED ALWAYS AS IDENTITY
                                PRIMARY KEY,
    mapping_id      INTEGER     NOT NULL,
    port            INTEGER     NOT NULL 
                                UNIQUE
);

ALTER TABLE servers.ports
ADD CONSTRAINT fk_port_mapping
FOREIGN KEY (mapping_id)
REFERENCES servers.ports_mapping(id);

END;