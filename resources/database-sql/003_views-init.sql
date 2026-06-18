BEGIN;

DROP VIEW IF EXISTS servers;

CREATE VIEW servers AS 
    SELECT s.name, s.steam_server_id, s.ram_limit, s.cpu_limit, p.host_port, p.container_port, pt.type 
    FROM servers.container AS s
    LEFT JOIN servers.ports_mapping AS mp 
        ON mp.server_id = s.id
    LEFT JOIN servers.ports AS p 
        ON p.mapping_id = mp.id
    LEFT JOIN servers.port_types AS pt 
        ON p.type_id = pt.id;

END;

BEGIN;

DROP VIEW IF EXISTS metrics.all_metrics CASCADE;
DROP VIEW IF EXISTS metrics CASCADE;

CREATE VIEW metrics.all_metrics AS
    SELECT p.time_id, p.container_id, p.cpu, p.ram, t.up, t.down 
    FROM metrics.performance AS p
    JOIN metrics.traffic AS t
        ON p.time_id = t.time_id AND p.container_id = t.container_id;

CREATE VIEW metrics AS
    SELECT s.name, t.time, m.cpu, m.ram, m.up, m.down 
    FROM metrics.timestamp AS t
    LEFT JOIN metrics.all_metrics AS m
        ON t.id = m.time_id
    JOIN servers.container AS s
        ON s.id = m.container_id;

END;