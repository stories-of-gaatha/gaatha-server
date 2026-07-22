from __future__ import annotations

from typing import Optional

import cv2
import strawberry
from django.db import models
from strawberry.types import Info


@strawberry.type
class FileFieldType:
    name: str
    url: str
    width: Optional[int]
    height: Optional[int]

    @staticmethod
    def resolve(file: models.FileField, info: Info) -> FileFieldType | None:
        if not file:
            return
        width = None
        height = None
        image = cv2.imread(file.path)
        if image is not None and image.any():
            height, width, _ = image.shape
        # TODO file width, height calculation is a heavy operation so it should be saved in the database in future.
        return FileFieldType(
            name=file.name,
            url=info.context['request'].build_absolute_uri(file.url),
            # TODO file width ,height calculation is a heavy operation so it should be saved in database in furute.
            width=width,
            height=height,
        )
