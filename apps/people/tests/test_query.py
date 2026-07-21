from apps.people.factories import PeopleFactory
from gaatha.tests import TestCase


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
