BEGIN;

DROP SCHEMA IF EXISTS metrics CASCADE;
CREATE SCHEMA IF NOT EXISTS metrics;

CREATE TABLE metrics.timestamp (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    time            TIMESTAMPTZ     NOT NULL 
                                    DEFAULT now()
);

CREATE TABLE metrics.performance (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    time_id         INTEGER         NOT NULL,
    container_id    INTEGER         NOT NULL,
    cpu             FLOAT(4)        NOT NULL,
    ram             FLOAT(4)        NOT NULL
);

ALTER TABLE metrics.performance
ADD CONSTRAINT fk_pm_pt
FOREIGN KEY (time_id) 
REFERENCES metrics.timestamp(id);

ALTER TABLE metrics.performance
ADD CONSTRAINT fk_pm_container
FOREIGN KEY (container_id) 
REFERENCES servers.container(id);

CREATE TABLE metrics.traffic (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    time_id         INTEGER         NOT NULL,
    container_id    INTEGER         NOT NULL,
    up              FLOAT(4)        NOT NULL,
    down            FLOAT(4)        NOT NULL
);

ALTER TABLE metrics.traffic
ADD CONSTRAINT fk_tm_pt
FOREIGN KEY (time_id) 
REFERENCES metrics.timestamp(id);

ALTER TABLE metrics.traffic
ADD CONSTRAINT fk_tm_container
FOREIGN KEY (container_id) 
REFERENCES servers.container(id);

END;