from apps.work.factories import WorkFactory, WorkImageFactory
from gaatha.tests import TestCase


class WorkQueryTestCase(TestCase):
    def test_works_query(self):
        works_query = """
            query MyQuery {
              works(pagination: {limit: 10}) {
                id
                title
                description
                area
                duration
                location
                status
                category {
                    id
                    name
                }
              }
            }
        """

        works = WorkFactory.create_batch(1)
        resp = self.query_check(works_query)
        self.assertEqual(
            [
                dict(
                    id=str(work.id),
                    title=work.title,
                    description=work.description,
                    area=work.area,
                    duration=work.duration,
                    location=work.location,
                    status=work.status,
                    category=dict(
                        id=str(work.category.id),
                        name=work.category.name,
                    ),
                )
                for work in works
            ],
            resp['data']['works'],
        )
        self.assertIsNotNone([work.cover_image] for work in works)
        self.assertIsNotNone([work.art_work] for work in works)

    def test_work_with_images_query(self):
        work_with_images_query = """
            query MyQuery($pk: ID!) {
              work(pk: $pk) {
                description
                duration
                id
                location
                status
                title
                isCoverImageDark
                images {
                    id
                    image {
                        name
                        url
                    }
                }
                area
                category {
                    id
                    name
                }
              }
            }
        """
        work = WorkFactory.create()
        WorkImageFactory.create_batch(3, work=work)
        resp_2 = self.query_check(work_with_images_query, variables={'pk': str(work.pk)})
        self.assertEqual(len(resp_2['data']['work']['images']), 3)
        self.assertIsNotNone([image['id']] for image in resp_2['data']['work']['images'])
        self.assertIsNotNone([image['image']] for image in resp_2['data']['work']['images'])
        self.assertEqual(resp_2['data']['work']['id'], str(work.id))
