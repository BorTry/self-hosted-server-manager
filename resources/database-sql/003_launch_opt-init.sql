BEGIN;

CREATE TABLE servers.launch_opts_mapping (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    name            VARCHAR(127)    NOT NULL,
    path            VARCHAR(127)    NOT NULL
                                    DEFAULT '',
    change_var      VARCHAR(127)    NOT NULL
                                    DEFAULT '',
    container_id    INTEGER         NOT NULL,
    handling        INTEGER         NOT NULL,
    source          INTEGER         NOT NULL
);

CREATE TABLE servers.launch_opts (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    mapping_id      INTEGER         NOT NULL,
    name            VARCHAR(127)    NOT NULL 
                                    DEFAULT '',
    value           VARCHAR(127)    NOT NULL 
                                    DEFAULT '',
    path            VARCHAR(127)    NOT NULL 
                                    DEFAULT ''
);

ALTER TABLE servers.launch_opts_mapping
ADD CONSTRAINT fk_lom_sc
FOREIGN KEY (container_id) 
REFERENCES servers.container(id);

ALTER TABLE servers.launch_opts
ADD CONSTRAINT fk_lo_lom
FOREIGN KEY (mapping_id) 
REFERENCES servers.launch_opts_mapping(id);

END;