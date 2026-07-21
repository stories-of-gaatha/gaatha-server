from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import Response
from strawberry.dataloader import DataLoader
from strawberry.django.views import AsyncGraphQLView

from apps.work.dataloaders import (
    load_work_image,
)


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, request: Request, response: Optional[Response]) -> Any:
        return {
            'request': request,
            'work_image_loader': DataLoader(load_fn=load_work_image),
        }
