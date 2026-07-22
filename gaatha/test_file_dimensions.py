from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.people.models import People
from apps.work.models import Work, WorkImage
from gaatha.models import compute_file_dimensions
from gaatha.tests import TestCase, generate_image_file
from gaatha.types import FileFieldType


class ComputeFileDimensionsTest(TestCase):
    def test_real_image_returns_dimensions(self):
        image = generate_image_file(size=(120, 80))
        self.assertEqual(compute_file_dimensions(image), (120, 80))

    def test_read_pointer_is_reset(self):
        # A subsequent storage save reads from the start, so the pointer must
        # be restored after we peek at the dimensions.
        image = generate_image_file(size=(10, 10))
        compute_file_dimensions(image)
        self.assertEqual(image.tell(), 0)

    def test_exif_rotated_image_returns_rendered_dimensions(self):
        # Orientation 6 = 90-degree rotation, so rendered w/h is swapped.
        # Matches how browsers display the image (and the old cv2 behaviour).
        rotated = generate_image_file('r.jpg', size=(120, 80), fmt='JPEG', orientation=6)
        self.assertEqual(compute_file_dimensions(rotated), (80, 120))

    def test_non_image_returns_none(self):
        non_image = SimpleUploadedFile('note.txt', b'not an image')
        self.assertEqual(compute_file_dimensions(non_image), (None, None))

    def test_empty_file_returns_none(self):
        self.assertEqual(compute_file_dimensions(None), (None, None))


class FileDimensionMixinTest(TestCase):
    """`FileField`s have no native width/height support, so the mixin fills them."""

    def test_filefield_image_dimensions_persisted(self):
        work = Work.objects.create(title='t', status='s', art_work=generate_image_file(size=(50, 30)))
        work.refresh_from_db()
        self.assertEqual((work.art_work_width, work.art_work_height), (50, 30))

    def test_filefield_non_image_dimensions_none(self):
        work = Work.objects.create(title='t', status='s', art_work=SimpleUploadedFile('a.txt', b'nope'))
        work.refresh_from_db()
        self.assertEqual((work.art_work_width, work.art_work_height), (None, None))

    def test_no_file_dimensions_none(self):
        work = Work.objects.create(title='t', status='s')
        self.assertEqual((work.art_work_width, work.art_work_height), (None, None))

    def test_changing_file_recomputes_dimensions(self):
        work = Work.objects.create(title='t', status='s', art_work=generate_image_file(size=(50, 30)))
        work.art_work = generate_image_file('other.png', size=(11, 22))
        work.save()
        work.refresh_from_db()
        self.assertEqual((work.art_work_width, work.art_work_height), (11, 22))

    def test_people_art_work_dimensions_persisted(self):
        person = People.objects.create(name='n', art_work=generate_image_file(size=(15, 25)))
        person.refresh_from_db()
        self.assertEqual((person.art_work_width, person.art_work_height), (15, 25))

    def test_unchanged_file_not_recomputed_on_save(self):
        # Loading from the DB and saving an unrelated field must not re-read
        # the file (the whole point: no per-save S3 fetch when nothing changed).
        work = Work.objects.create(title='t', status='s', art_work=generate_image_file(size=(50, 30)))
        reloaded = Work.objects.get(pk=work.pk)
        with mock.patch('gaatha.models.compute_file_dimensions') as compute:
            reloaded.title = 'updated'
            reloaded.save()
            compute.assert_not_called()

    def test_unchanged_non_image_file_not_recomputed_on_save(self):
        # Non-image files (e.g. SVG art_work) yield no dimensions, but an
        # unchanged one must still never be re-read on later saves.
        work = Work.objects.create(title='t', status='s', art_work=SimpleUploadedFile('a.txt', b'nope'))
        reloaded = Work.objects.get(pk=work.pk)
        with mock.patch('gaatha.models.compute_file_dimensions') as compute:
            reloaded.title = 'updated'
            reloaded.save()
            compute.assert_not_called()

    def test_update_fields_includes_recomputed_dimensions(self):
        # A targeted save(update_fields=...) after replacing the file must
        # persist the recomputed dimensions, not silently drop them.
        work = Work.objects.create(title='t', status='s', art_work=generate_image_file(size=(50, 30)))
        work.art_work = generate_image_file('new.png', size=(11, 22))
        work.save(update_fields=['art_work'])
        work.refresh_from_db()
        self.assertEqual((work.art_work_width, work.art_work_height), (11, 22))


class ImageFieldDimensionTest(TestCase):
    """`ImageField` dimensions are persisted by the mixin at save time."""

    def test_cover_image_dimensions_persisted(self):
        work = Work.objects.create(title='t', status='s', cover_image=generate_image_file(size=(200, 100)))
        work.refresh_from_db()
        self.assertEqual((work.cover_image_width, work.cover_image_height), (200, 100))

    def test_work_image_dimensions_persisted(self):
        work = Work.objects.create(title='t', status='s')
        work_image = WorkImage.objects.create(work=work, image=generate_image_file(size=(64, 48)))
        work_image.refresh_from_db()
        self.assertEqual((work_image.image_width, work_image.image_height), (64, 48))

    def test_profile_picture_dimensions_persisted(self):
        person = People.objects.create(name='n', profile_picture=generate_image_file(size=(33, 44)))
        person.refresh_from_db()
        self.assertEqual((person.profile_picture_width, person.profile_picture_height), (33, 44))


class _FakeRequest:
    def build_absolute_uri(self, url):
        return f'http://testserver{url}'


class _FakeInfo:
    context = {'request': _FakeRequest()}


class _S3LikeFieldFile:
    """Mimics a remote file: has name/url but no local path, and blows up if read."""

    name = 'work/art-works/x.png'
    url = '/media/work/art-works/x.png'

    def __bool__(self):
        return True

    @property
    def path(self):
        raise NotImplementedError('remote storage has no local path')

    def open(self, *args, **kwargs):
        raise AssertionError('resolve must not open the file')

    def read(self, *args, **kwargs):
        raise AssertionError('resolve must not read the file')


class FileFieldTypeResolveTest(TestCase):
    def test_resolve_serves_stored_dimensions_without_touching_file(self):
        result = FileFieldType.resolve(_S3LikeFieldFile(), _FakeInfo(), 120, 80)
        self.assertEqual((result.width, result.height), (120, 80))
        self.assertEqual(result.name, 'work/art-works/x.png')
        self.assertEqual(result.url, 'http://testserver/media/work/art-works/x.png')

    def test_resolve_returns_none_for_empty_file(self):
        self.assertIsNone(FileFieldType.resolve(None, _FakeInfo()))
