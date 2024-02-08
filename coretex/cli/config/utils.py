from typing import TypeVar, Type, Any, Optional, Dict


KeyType = TypeVar("KeyType")
GetType = TypeVar("GetType")


def typedGet(
    container: Dict[KeyType, Any],
    key: KeyType,
    type_: Type[GetType]
) -> GetType:

    value = container.get(key)

    if not isinstance(value, type_):
        raise TypeError("Type error....")  # TODO

    return value
