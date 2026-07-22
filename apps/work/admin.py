from django.contrib import admin

from .forms import WorkForm
from .models import Work, WorkCategory, WorkImage


class WorkImageInline(admin.TabularInline):
    model = WorkImage
    extra = 1


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

    inlines = [
        WorkImageInline,
    ]


@admin.register(WorkCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
