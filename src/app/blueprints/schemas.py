from marshmallow import Schema, fields

class ContainerResponseSchema(Schema):
    containers=                 fields.List(fields.Dict())

class ContainerStartSchema(Schema):
    launch_opts=                fields.Dict(keys=fields.Str(), values=fields.Str())

class ContainerAddSchema(Schema):
    server_name =               fields.String()
    ports =                     fields.String()
    restrict_ports =            fields.Bool()
    port_type =                 fields.Bool()
    strict_ports =              fields.Bool()
    forward_ports =             fields.Bool()
    steam_server =              fields.String()
    steam_id =                  fields.String()
    cpu_limit =                 fields.Integer()
    ram_limit =                 fields.Decimal()
    launch_opt =                fields.String()
    install_opt =               fields.String()

class ContainerImage(Schema):
    image =                     fields.Raw()