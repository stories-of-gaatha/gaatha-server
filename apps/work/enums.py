import strawberry

from .models import Work

WorkTypeEnum = strawberry.enum(Work.WorkType, name="WorkTypeEnum")
