from django.db import models
from PIL import Image

# EXIF orientation values 5-8 mean the image is rotated 90/270 degrees, so the
# rendered dimensions are the stored width/height swapped.
_EXIF_ORIENTATION_TAG = 0x0112
_EXIF_SWAPPED_ORIENTATIONS = frozenset({5, 6, 7, 8})


def compute_file_dimensions(file) -> tuple[int | None, int | None]:
    """Return the rendered (width, height) of an image file, else (None, None).

    Honors EXIF orientation so the result matches how browsers display the
    image (the previous cv2-based resolver applied orientation too). Only the
    header/EXIF is read -- no full decode. Reads the file once and restores the
    read pointer so a subsequent storage save is not corrupted. Non-image files
    return (None, None).
    """
    if not file:
        return None, None
    # If we open a closed (stored) file we must close it again to avoid leaking
    # handles/connections (e.g. per-row during the backfill migration over S3).
    # An already-open file is an in-flight upload -- leave it open and only
    # rewind it so the subsequent storage save reads from the start.
    was_closed = file.closed
    try:
        file.open()
        image = Image.open(file)
        width, height = image.size
        if image.getexif().get(_EXIF_ORIENTATION_TAG, 1) in _EXIF_SWAPPED_ORIENTATIONS:
            width, height = height, width
    except Exception:
        return None, None
    finally:
        try:
            file.close() if was_closed else file.seek(0)
        except Exception:
            pass
    return width, height


class FileDimensionMixin(models.Model):
    """Persist file/image dimensions at save time so they never have to be read
    from storage on the request path.

    Covers both ``ImageField`` and plain ``FileField`` (which may or may not
    hold an image). Dimensions are (re)computed only when the file is newly set
    or replaced -- an unchanged file is never re-read, even one that yields no
    dimensions (e.g. an SVG in a ``FileField``). Set ``FILE_DIMENSION_FIELDS``
    to a mapping of ``file_field -> (width_field, height_field)``.
    """

    FILE_DIMENSION_FIELDS: dict[str, tuple[str, str]] = {}

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_files = {field: (getattr(self, field).name or None) for field in self.FILE_DIMENSION_FIELDS}

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        update_fields = set(update_fields) if update_fields is not None else None
        # A brand-new row's file arrives via __init__, so `changed` is False for
        # it; `_state.adding` catches that first insert.
        is_new = self._state.adding
        for field, (width_attr, height_attr) in self.FILE_DIMENSION_FIELDS.items():
            file = getattr(self, field)
            current = (file.name or None) if file else None
            changed = current != self._original_files.get(field)
            if changed or (is_new and current):
                width, height = compute_file_dimensions(file)
                setattr(self, width_attr, width)
                setattr(self, height_attr, height)
                self._original_files[field] = current
                if update_fields is not None:
                    update_fields.update((width_attr, height_attr))
        if update_fields is not None:
            kwargs["update_fields"] = update_fields
        super().save(*args, **kwargs)
