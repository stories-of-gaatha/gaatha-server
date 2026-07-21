from typing import Optional

import strawberry
import strawberry_django
from strawberry import auto
from strawberry.types import Info

from gaatha.types import FileFieldType
from gaatha.utils import get_enum_label

from .enums import WorkTypeEnum
from .filters import WorkFilter
from .models import (
    Work,
    WorkCategory,
    WorkImage,
)


@strawberry_django.ordering.order(Work)
class WorkOrderType:
    order: auto


@strawberry.django.type(WorkCategory)
class WorkCategoryType:
    id: auto
    name: auto


@strawberry.django.type(WorkImage)
class WorkImageType:
    id: auto

    @strawberry.field
    async def image(self, info: Info) -> FileFieldType | None:
        return FileFieldType.resolve(self.image, info)


@strawberry.django.type(Work)
class WorkType:
    id: auto
    title: auto
    work_type: WorkTypeEnum
    sub_title: auto
    description: auto
    area: auto
    status: auto
    duration: auto
    location: auto
    category: WorkCategoryType
    is_cover_image_dark: auto
    order: auto

    @strawberry.field
    async def art_work(self, info: Info) -> FileFieldType | None:
        return FileFieldType.resolve(self.art_work, info)

    @strawberry.field
    async def cover_image(self, info: Info) -> FileFieldType | None:
        return FileFieldType.resolve(self.cover_image, info)

    @strawberry.field
    async def images(self, info: Info) -> list[WorkImageType]:
        return await info.context["work_image_loader"].load(self.id)

    @strawberry.field
    async def work_type_label(self, info: Info) -> Optional[str]:
        return get_enum_label(WorkTypeEnum, self.work_type)


@strawberry.django.type(Work, pagination=True, filters=WorkFilter)
class WorkListType(WorkType):
    pass


@strawberry.type
class FilterChoiceType:
    work_category: list[WorkCategoryType] | None
