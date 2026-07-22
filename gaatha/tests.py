import io
from typing import Dict

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase as BaseTestCase
from PIL import Image


def generate_image_file(name: str = 'test.png', size: tuple[int, int] = (120, 80), fmt: str = 'PNG', orientation=None):
    """Build an in-memory uploaded image of the given pixel size for tests.

    Pass ``orientation`` (an EXIF orientation value) to tag the JPEG with a
    rotation, e.g. 6 for a 90-degree turn.
    """
    buffer = io.BytesIO()
    image = Image.new('RGB', size, 'red')
    save_kwargs = {}
    if orientation is not None:
        exif = image.getexif()
        exif[0x0112] = orientation
        save_kwargs['exif'] = exif
    image.save(buffer, fmt, **save_kwargs)
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type=f'image/{fmt.lower()}')


class TestCase(BaseTestCase):
    TEST_LANGUAGES = (
        'en',
        'fr',
    )

    def force_login(self, user):
        self.client.force_login(user)

    def logout(self):
        self.client.logout()

    def query_check(
        self,
        query: str,
        with_assert: bool = True,
        variables: dict | None = None,
        **kwargs,
    ) -> Dict:
        response = self.client.post(
            "/graphql/",
            data={
                "query": query,
                "variables": variables,
            },
            content_type="application/json",
            **kwargs,
        )
        if with_assert:
            self.assertEqual(response.status_code, 200)
        return response.json()

    def assertResponseNoErrors(self, resp, msg=None):
        """
        Assert that the call went through correctly. 200 means the syntax is ok,
        if there are no `errors`,
        the call was fine.
        :resp HttpResponse: Response
        """
        content = resp.json()
        self.assertEqual(resp.status_code, 200, msg or content)
        self.assertNotIn("errors", list(content.keys()), msg or content)

    def assertResponseHasErrors(self, resp, msg=None):
        """
        Assert that the call was failing. Take care: Even with errors,
        GraphQL returns status 200!
        :resp HttpResponse: Response
        """
        content = resp.json()
        self.assertIn("errors", list(content.keys()), msg or content)


class FakeTest(TestCase):
    """
    This test is for running migrations only
    docker-compose run --rm server ./manage.py test -v 2 --pattern="gaatha/tests.py"
    """

    def test_fake(self):
        pass
