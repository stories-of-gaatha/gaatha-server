from typing import Optional

import strawberry

from .enums import WorkTypeEnum
from .models import Work


@strawberry.django.filters.filter(Work)
class WorkFilter:
    category: Optional[strawberry.ID]
    work_type: Optional[WorkTypeEnum]
