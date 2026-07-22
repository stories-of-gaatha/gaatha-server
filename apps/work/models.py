from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from gaatha.models import FileDimensionMixin


class WorkCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Work(FileDimensionMixin, models.Model):
    FILE_DIMENSION_FIELDS = {
        "art_work": ("art_work_width", "art_work_height"),
        "cover_image": ("cover_image_width", "cover_image_height"),
    }

    class WorkType(models.TextChoices):
        ARCHITECTURE = 'architecture', 'Architecture'
        GRAPHICS_AND_VISUALIZATION = 'graphics_and_visualizations', 'Graphics and Visualizations'

    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=225, blank=True)
    work_type = models.CharField(max_length=225, choices=WorkType.choices, default=WorkType.ARCHITECTURE)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    art_work = models.FileField(null=True, blank=True, upload_to="work/art-works")
    art_work_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    art_work_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    is_cover_image_dark = models.BooleanField(default=False, verbose_name=_('Is Cover Image Dark ?'))
    cover_image = models.ImageField(null=True, blank=True, upload_to="work/cover-images", verbose_name=_('Cover image'))
    cover_image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    cover_image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    area = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(
        WorkCategory, verbose_name=_('Category'), on_delete=models.SET_NULL, blank=True, null=True, related_name='work_category'
    )
    status = models.CharField(max_length=250, verbose_name=_('Status'))
    duration = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Work"
        verbose_name_plural = "Works"

    def __str__(self):
        return str(self.id)

    def clean(self):
        if self.work_type == Work.WorkType.GRAPHICS_AND_VISUALIZATION and self.category:
            raise ValidationError({'category': "Cannot select category when work type is Graphics and Visualization"})


class WorkImage(FileDimensionMixin, models.Model):
    FILE_DIMENSION_FIELDS = {"image": ("image_width", "image_height")}

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='workimage_work', verbose_name=_('Work'))
    image = models.ImageField(upload_to="work-image/images/", verbose_name=_('Image'))
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)

    def __str__(self):
        return str(self.work.title)
