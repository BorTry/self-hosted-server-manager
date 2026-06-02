BEGIN;

DROP SCHEMA IF EXISTS servers CASCADE;
CREATE SCHEMA IF NOT EXISTS servers;

CREATE TABLE servers.container (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY
                                    PRIMARY KEY,
    name            VARCHAR(127)    NOT NULL
                                    UNIQUE,
    ram_limit       DECIMAL(5, 2)        ,
    cpu_limit       INTEGER         
);

CREATE TABLE servers.ports_mapping (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY
                                    PRIMARY KEY,
    server_id       INTEGER         NOT NULL,
    ports_open      BOOLEAN         NOT NULL
                                    DEFAULT FALSE,
    strict_ports    BOOLEAN         NOT NULL
                                    DEFAULT FALSE,
    do_port_forward BOOLEAN         NOT NULL
                                    DEFAULT FALSE,
    success_port    BOOLEAN         
);

ALTER TABLE servers.ports_mapping
ADD CONSTRAINT fk_mapping_container
FOREIGN KEY (server_id)
REFERENCES servers.container(id);

CREATE TABLE servers.ports (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY
                                    PRIMARY KEY,
    mapping_id      INTEGER         NOT NULL,
    port            INTEGER         NOT NULL 
                                    UNIQUE,
    type_id         INTEGER         NOT NULL    
);

ALTER TABLE servers.ports
ADD CONSTRAINT fk_port_mapping
FOREIGN KEY (mapping_id)
REFERENCES servers.ports_mapping(id);

ALTER TABLE servers.ports
ADD CONSTRAINT fk_port_type
FOREIGN KEY (type_id)
REFERENCES servers.port_types(id);

CREATE TABLE servers.port_types (
    id              INTEGER         PRIMARY KEY,
    type            VARCHAR(3)      
)

INSERT INTO servers.port_types (id, type)
VALUES 
    (0, "TCP"),
    (1, "UDP"),
    (2,  NULL),

END;