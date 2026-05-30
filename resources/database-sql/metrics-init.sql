BEGIN;

DROP TABLE IF EXISTS metric_timestamp, performance_metric, traffic_metric;

CREATE TABLE container (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY
                                    PRIMARY KEY,
    name            VARCHAR(127)    NOT NULL
                                    UNIQUE
);

CREATE TABLE metric_timestamp (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    time            TIMESTAMPTZ     NOT NULL 
                                    DEFAULT now()
);

CREATE TABLE performance_metric (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    time_id         INTEGER         NOT NULL,
    container_id    INTEGER         NOT NULL,
    cpu             FLOAT(4)        NOT NULL,
    ram             FLOAT(4)        NOT NULL
);

ALTER TABLE performance_metric
ADD CONSTRAINT fk_pm_pt
FOREIGN KEY (time_id) 
REFERENCES metric_timestamp(id);

ALTER TABLE performance_metric
ADD CONSTRAINT fk_pm_container
FOREIGN KEY (container_id) 
REFERENCES container(id);

CREATE TABLE traffic_metric (
    id              INTEGER         GENERATED ALWAYS AS IDENTITY 
                                    PRIMARY KEY,
    time_id         INTEGER         NOT NULL,
    container_id    INTEGER         NOT NULL,
    up              FLOAT(4)        NOT NULL,
    down            FLOAT(4)        NOT NULL
);

ALTER TABLE traffic_metric
ADD CONSTRAINT fk_tm_pt
FOREIGN KEY (time_id) 
REFERENCES metric_timestamp(id);

ALTER TABLE traffic_metric
ADD CONSTRAINT fk_tm_container
FOREIGN KEY (container_id) 
REFERENCES container(id);

END;