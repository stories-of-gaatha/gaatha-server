from django.contrib import admin

from .models import People


@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'designation',
        'email',
        'is_current_employee',
        'is_founder',
        'order',
    ]
    readonly_fields = [
        'profile_picture_width',
        'profile_picture_height',
        'art_work_width',
        'art_work_height',
    ]
