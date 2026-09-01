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
    SELECT p.time_id, p.container_id, p.cpu, p.ram, t.upload, t.download 
    FROM metrics.performance AS p
    JOIN metrics.traffic AS t
        ON p.time_id = t.time_id AND p.container_id = t.container_id;

CREATE VIEW metrics AS
    SELECT s.name, t.time, m.cpu, m.ram, m.upload, m.download 
    FROM metrics.timestamp AS t
    LEFT JOIN metrics.all_metrics AS m
        ON t.id = m.time_id
    JOIN servers.container AS s
        ON s.id = m.container_id;

END;

BEGIN;

DROP VIEW IF EXISTS launch_opts;

CREATE VIEW launch_opts AS
    SELECT lo.id, lo.value, lo.name as lo_name, lo.path, lom.handling, lom.source, lom.change_var, lom.path as file_path, lom.var_flag, lom.name as lom_name, s.name as s_name
    FROM servers.launch_opts AS lo
    LEFT JOIN servers.launch_opts_mapping AS lom
        ON lo.mapping_id = lom.id
    LEFT JOIN servers.container as s
        ON lom.container_id = s.id;
    
END;