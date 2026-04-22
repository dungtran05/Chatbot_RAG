from bson import ObjectId


def serialize_id(value: ObjectId | str) -> str:
    return str(value)

