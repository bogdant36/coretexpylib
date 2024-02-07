from typing import TypeVar, Type, Any, Optional, Dict


KeyType = TypeVar("KeyType")
GetType = TypeVar("GetType")


def typedGet(
    container: Dict[KeyType, Any],
    key: KeyType,
    type_: Type[GetType],
    default: Optional[GetType] = None
) -> Optional[GetType]:

    value = container.get(key)

    if value is None:
        return default

    if not isinstance(value, type_):
        return default

    return value
