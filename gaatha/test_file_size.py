from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import TestCase

from apps.people.models import People
from apps.work.models import Work, WorkImage
from gaatha.utils import MAX_FILE_SIZE_MB, FileSizeValidator, validate_file_size

ONE_MB = 1024 * 1024


def _uploaded_file(size_bytes: int, name: str = 'test.jpg') -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b'x' * size_bytes, content_type='image/jpeg')


class ValidateFileSizeTest(TestCase):
    def test_file_within_limit_is_accepted(self):
        validate_file_size(_uploaded_file(ONE_MB), 3)

    def test_file_exactly_at_limit_is_accepted(self):
        validate_file_size(_uploaded_file(3 * ONE_MB), 3)

    def test_file_over_limit_is_rejected(self):
        with self.assertRaises(ValidationError) as cm:
            validate_file_size(_uploaded_file(3 * ONE_MB + 1), 3)
        self.assertIn('Max file size must be less than 3 MB', str(cm.exception))

    def test_empty_file_is_skipped(self):
        """Model fields with no file must not blow up on `file.size`."""
        validate_file_size(None, 3)
        validate_file_size(People().profile_picture, 3)


class FileSizeValidatorTest(TestCase):
    def test_defaults_to_project_limit(self):
        self.assertEqual(FileSizeValidator().max_size, MAX_FILE_SIZE_MB)

    def test_rejects_over_its_own_limit(self):
        validator = FileSizeValidator(1)
        validator(_uploaded_file(ONE_MB))
        with self.assertRaises(ValidationError):
            validator(_uploaded_file(ONE_MB + 1))

    def test_is_serializable_and_comparable(self):
        """`deconstruct`/`__eq__` keep migrations stable (no spurious AlterField)."""
        path, args, kwargs = FileSizeValidator(5).deconstruct()
        self.assertEqual(path, 'gaatha.utils.FileSizeValidator')
        self.assertEqual((args, kwargs), ((5,), {}))
        self.assertEqual(FileSizeValidator(5), FileSizeValidator(5))
        self.assertNotEqual(FileSizeValidator(5), FileSizeValidator(3))


class ModelFileFieldsTest(TestCase):
    def test_every_file_field_has_a_size_validator(self):
        """Guard so a newly added file/image field can't skip the size limit."""
        missing = [
            f'{model._meta.label}.{field.name}'
            for model in apps.get_models()
            if model._meta.app_label in ('people', 'work')
            for field in model._meta.get_fields()
            if isinstance(field, models.FileField)
            and not any(isinstance(validator, FileSizeValidator) for validator in field.validators)
        ]
        self.assertEqual(missing, [])

    def test_full_clean_rejects_oversized_upload(self):
        oversized = _uploaded_file((MAX_FILE_SIZE_MB + 1) * ONE_MB)

        for instance, field in [
            (People(name='x', profile_picture=oversized), 'profile_picture'),
            (People(name='x', art_work=oversized), 'art_work'),
            (Work(title='x', status='x', art_work=oversized), 'art_work'),
            (Work(title='x', status='x', cover_image=oversized), 'cover_image'),
            (WorkImage(image=oversized), 'image'),
        ]:
            with self.subTest(model=type(instance).__name__, field=field):
                with self.assertRaises(ValidationError) as cm:
                    instance.full_clean()
                self.assertIn(field, cm.exception.message_dict)
                self.assertIn(
                    f'Max file size must be less than {MAX_FILE_SIZE_MB} MB',
                    str(cm.exception.message_dict[field]),
                )
