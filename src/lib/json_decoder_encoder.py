from json import JSONDecoder, JSONEncoder

CLASS_REGISTRY = {}


class decoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            object_hook=self.object_hook,
            **kwargs
        )

    def object_hook(self, data):
        type_name = data.pop("__type__", None)

        if type_name is None:
            return data

        cls = CLASS_REGISTRY.get(type_name)

        if cls is None:
            return data

        fields = {k: v for k, v in data.items() if (k != "__type__" and k[0] != "_")}
    
        return cls(**fields)

class encoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            data = dict(obj.__dict__)
        else:
            data = {}

        for slot in get_all_slots(obj):
            if slot in ("__dict__", "__weakref__"):
                continue

            if hasattr(obj, slot):
                data[slot] = getattr(obj, slot)

        data["__type__"] = type(obj).__name__

        return data
    
def register(cls):
    CLASS_REGISTRY[cls.__name__] = cls
    return cls

def get_all_slots(obj):
    slots = []

    for cls in type(obj).__mro__:
        cls_slots = getattr(cls, "__slots__", ())

        if isinstance(cls_slots, str):
            cls_slots = (cls_slots,)

        slots.extend(cls_slots)

    return slots