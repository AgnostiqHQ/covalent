import cloudpickle
import orjson as json


def cloudpickle_serialize(obj):
    return cloudpickle.dumps(obj)


def cloudpickle_deserialize(obj):
    return cloudpickle.loads(obj)


def dummy_serialize(obj):
    try:
        return [o.json() for o in obj]
    except (AttributeError, TypeError):
        return obj


def dummy_deserialize(ser_obj):
    try:
        return [json.loads(ser_o) for ser_o in ser_obj]
    except (json.JSONDecodeError, TypeError):
        return ser_obj


def select_first_executor(qnode, executors):
    """Selects the first executor to run the qnode"""
    return executors[0]
