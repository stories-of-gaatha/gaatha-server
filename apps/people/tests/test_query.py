from apps.people.factories import PeopleFactory
from gaatha.tests import TestCase, generate_image_file


class PeopleQueryTestCase(TestCase):
    def test_people_query(self):
        people_query = """
            query MyQuery {
              people(pagination: {limit: 10}) {
                id
                designation
                email
                isFounder
                instagramUrl
                isCurrentEmployee
                linkedinUrl
                name
                qualification
                }
            }
        """

        people = PeopleFactory.create_batch(3)
        resp = self.query_check(people_query)
        self.assertEqual(
            [
                dict(
                    id=str(person.id),
                    designation=person.designation,
                    email=person.email,
                    instagramUrl=person.instagram_url,
                    isCurrentEmployee=person.is_current_employee,
                    isFounder=person.is_founder,
                    linkedinUrl=person.linkedin_url,
                    name=person.name,
                    qualification=person.qualification,
                )
                for person in people
            ],
            resp['data']['people'],
        )
        self.assertIsNotNone([person.profile_picture] for person in people)
        self.assertIsNotNone([person.art_work] for person in people)

    def test_file_dimensions_served_from_db(self):
        file_dimensions_query = """
            query MyQuery {
              people(pagination: {limit: 10}) {
                profilePicture { width height }
                artWork { width height }
              }
            }
        """
        PeopleFactory.create(
            profile_picture=generate_image_file('pp.png', size=(33, 44)),
            art_work=generate_image_file('aw.png', size=(15, 25)),
        )
        resp = self.query_check(file_dimensions_query)
        person = resp['data']['people'][0]
        self.assertEqual(person['profilePicture'], dict(width=33, height=44))
        self.assertEqual(person['artWork'], dict(width=15, height=25))
