from django.db import migrations

from gaatha.models import compute_file_dimensions


def backfill(apps, schema_editor):
    People = apps.get_model('people', 'People')

    for person in People.objects.all().iterator():
        person.profile_picture_width, person.profile_picture_height = compute_file_dimensions(
            person.profile_picture
        )
        person.art_work_width, person.art_work_height = compute_file_dimensions(person.art_work)
        person.save(
            update_fields=[
                'profile_picture_width', 'profile_picture_height',
                'art_work_width', 'art_work_height',
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_people_art_work_height_people_art_work_width_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
