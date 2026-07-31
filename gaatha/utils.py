from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.deconstruct import deconstructible
from strawberry.enum import EnumType


def get_enum_label(
    enum_type: EnumType,
    value: str,
    default_description='',
) -> str:
    if value:
        return enum_type(value).label
    return default_description


MAX_FILE_SIZE_MB = 3


def validate_file_size(file: File, max_size: int) -> None:
    """
    This function validates that a given uploaded file does not exceed
    the specified size limit.

    Args:
        file: The uploaded file to validate.
        max_size: Maximum allowed file size in megabytes.

    Raises:
        ValidationError: If the file size exceeds the allowed limit.
    """
    if not file:
        return

    max_size_bytes = max_size * 1024 * 1024  # Convert MB to bytes

    if file.size > max_size_bytes:
        raise ValidationError(
            f"File is too large. Max file size must be less than {max_size} MB.",
        )


@deconstructible
class FileSizeValidator:
    """Model-field validator wrapper around :func:`validate_file_size`.

    Field validators are serialized into migrations, so this must be a
    deconstructible callable (not a lambda/partial). ``__eq__`` keeps
    makemigrations from emitting a no-op field alteration on every run.
    """

    def __init__(self, max_size: int = MAX_FILE_SIZE_MB):
        self.max_size = max_size

    def __call__(self, file: File) -> None:
        validate_file_size(file, self.max_size)

    def __eq__(self, other) -> bool:
        return isinstance(other, FileSizeValidator) and self.max_size == other.max_size

    def __hash__(self) -> int:
        return hash(self.max_size)
