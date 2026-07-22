from django.contrib import admin

from .forms import WorkForm
from .models import Work, WorkCategory, WorkImage


class WorkImageInline(admin.TabularInline):
    model = WorkImage
    extra = 1
    readonly_fields = ['image_width', 'image_height']


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    form = WorkForm
    list_display = [
        'title',
        'work_type',
        'status',
        'category',
        'status',
        'duration',
        'order',
    ]
    readonly_fields = [
        'art_work_width',
        'art_work_height',
        'cover_image_width',
        'cover_image_height',
    ]

    inlines = [
        WorkImageInline,
    ]


@admin.register(WorkCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
