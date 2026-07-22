import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import fuzzy
from factory.django import DjangoModelFactory

from .models import (
    Work,
    WorkCategory,
    WorkImage,
)


class WorkCategoryFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText(length=15)

    class Meta:
        model = WorkCategory


class WorkFactory(DjangoModelFactory):
    category = factory.SubFactory(WorkCategoryFactory)
    cover_image = SimpleUploadedFile('test.jpg', b'whatevercontentsyouwant')
    art_work = SimpleUploadedFile('test.jpg', b'whatevercontentsyouwant')
    title = fuzzy.FuzzyText(length=15)
    description = fuzzy.FuzzyText(length=50)
    area = fuzzy.FuzzyText(length=50)
    status = fuzzy.FuzzyText(length=50)
    duration = fuzzy.FuzzyText(length=50)
    location = fuzzy.FuzzyText(length=50)
    is_cover_image_dark = True

    class Meta:
        model = Work


class WorkImageFactory(DjangoModelFactory):
    work = factory.SubFactory(WorkFactory)
    image = SimpleUploadedFile('test.jpg', b'whatevercontentsyouwant')

    class Meta:
        model = WorkImage
