from django.db import migrations

from gaatha.models import compute_file_dimensions


def backfill(apps, schema_editor):
    Work = apps.get_model('work', 'Work')
    WorkImage = apps.get_model('work', 'WorkImage')

    for work in Work.objects.all().iterator():
        work.art_work_width, work.art_work_height = compute_file_dimensions(work.art_work)
        work.cover_image_width, work.cover_image_height = compute_file_dimensions(work.cover_image)
        work.save(
            update_fields=[
                'art_work_width', 'art_work_height',
                'cover_image_width', 'cover_image_height',
            ]
        )

    for image in WorkImage.objects.all().iterator():
        image.image_width, image.image_height = compute_file_dimensions(image.image)
        image.save(update_fields=['image_width', 'image_height'])


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0007_work_art_work_height_work_art_work_width_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
