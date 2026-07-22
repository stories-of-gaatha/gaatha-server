from apps.work.factories import WorkFactory, WorkImageFactory
from gaatha.tests import TestCase, generate_image_file


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

    def test_file_dimensions_served_from_db(self):
        file_dimensions_query = """
            query MyQuery($pk: ID!) {
              work(pk: $pk) {
                coverImage { width height }
                artWork { width height }
                images { image { width height } }
              }
            }
        """
        work = WorkFactory.create(
            cover_image=generate_image_file('cover.png', size=(200, 100)),
            art_work=generate_image_file('art.png', size=(40, 60)),
        )
        WorkImageFactory.create(work=work, image=generate_image_file('wi.png', size=(64, 48)))
        resp = self.query_check(file_dimensions_query, variables={'pk': str(work.pk)})
        data = resp['data']['work']
        self.assertEqual(data['coverImage'], dict(width=200, height=100))
        self.assertEqual(data['artWork'], dict(width=40, height=60))
        self.assertEqual(data['images'][0]['image'], dict(width=64, height=48))
