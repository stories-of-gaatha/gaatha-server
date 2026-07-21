from collections import defaultdict

from asgiref.sync import sync_to_async

from apps.work.models import (
    WorkImage,
)


def work_image_load(keys: list[int]):
    qs = WorkImage.objects.filter(work__in=keys)
    _map = defaultdict(list)
    for workimage in qs:
        _map[workimage.work.id].append(workimage)
    return [_map[key] for key in keys]


load_work_image = sync_to_async(work_image_load)
