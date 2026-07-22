from __future__ import annotations

from typing import Optional

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
    def resolve(
        file: models.FileField,
        info: Info,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> FileFieldType | None:
        # width/height are persisted on the model at upload time (see
        # gaatha.models.FileDimensionMixin and ImageField width/height fields)
        # so we never open the file here — avoids a per-request read on S3.
        if not file:
            return
        return FileFieldType(
            name=file.name,
            url=info.context['request'].build_absolute_uri(file.url),
            width=width,
            height=height,
        )
