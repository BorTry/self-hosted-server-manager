from marshmallow import Schema, fields, validates_schema, ValidationError
from flask_smorest.fields import Upload

ALLOWED_EXTENSIONS = {"jpg", "png"}

class ContainerResponseSchema(Schema):
    containers =                fields.List(fields.Dict())

class ContainerStartSchema(Schema):
    launch_opts =               fields.Dict(keys=fields.Str(), values=fields.Str())

class ContainerAddSchema(Schema):
    server_name =               fields.String(required=True)
    port_mapping =              fields.List(fields.String(), required=True)
    strict_ports =              fields.Bool(load_default=False)
    forwards_ports =            fields.Bool(load_default=False)
    steam_server =              fields.Bool(load_default=False)
    steam_id =                  fields.String(allow_none=True, load_default="")
    cpu_limit =                 fields.Integer(required=True)
    ram_limit =                 fields.Decimal(required=True, as_string=True)
    launch_opt =                fields.String(allow_none=True, load_default="")
    install_opt =               fields.String(allow_none=True, load_default="")

class ContainerImage(Schema):
    image =                     Upload(allow_none=True)

    @validates_schema
    def validate_image(self, data, **kwargs):
        image = data["image"]

        if image.filename == "":
            return # image wasnt given

        ext = image.filename.rsplit(".", 1)[-1].lower()
        if "." not in image.filename or ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid image type", field_name="image")