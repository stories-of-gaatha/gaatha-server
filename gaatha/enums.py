from typing import Generic, TypeVar

import strawberry

GenericEnumVar = TypeVar('GenericEnumVar')


@strawberry.type
class GenericEnumValue(Generic[GenericEnumVar]):
    name: str
    label: str


def generate_enum_name_and_label(enum_class) -> list[GenericEnumValue]:
    """
    Return list of generic enum value
    """
    return [GenericEnumValue(name=enum_item.name, label=enum_item.label) for enum_item in enum_class]
