import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import fuzzy
from factory.django import DjangoModelFactory

from .models import People


class PeopleFactory(DjangoModelFactory):
    profile_picture = SimpleUploadedFile('test.jpg', b'whatevercontentsyouwant')
    art_work = SimpleUploadedFile('test.jpg', b'whatevercontentsyouwant')
    name = fuzzy.FuzzyText(length=15)
    email = factory.Sequence(lambda n: f'{n}@xyz.com')
    designation = fuzzy.FuzzyText(length=50)
    qualification = fuzzy.FuzzyText(length=50)
    is_current_employee = True
    is_founder = True
    linkedin_url = factory.Sequence(lambda n: f'https://www.linkedin.com/{n}')
    instagram_url = factory.Sequence(lambda n: f'https://www.instagram.com/{n}')

    class Meta:
        model = People
