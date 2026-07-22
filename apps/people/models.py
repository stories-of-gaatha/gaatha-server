from django.db import models
from django.utils.translation import gettext_lazy as _


class People(models.Model):
    name = models.CharField(max_length=250, verbose_name=_('Name'))
    profile_picture = models.ImageField(blank=True, upload_to="people/profile-pictures", verbose_name=_("Profile Picture"))
    art_work = models.FileField(blank=True, upload_to="people/art-works", verbose_name=_("Art Work"))
    order = models.PositiveIntegerField(blank=True, null=True)
    email = models.EmailField(max_length=250, blank=True, verbose_name=_('Email'))
    designation = models.CharField(max_length=100, blank=True, verbose_name=_("Designation"))
    qualification = models.CharField(max_length=250, blank=True, verbose_name=_("Qualification"))
    is_current_employee = models.BooleanField(default=True, verbose_name=_("Is Current Employee"))
    is_founder = models.BooleanField(default=False, verbose_name=_("Is Founding Member"))
    linkedin_url = models.URLField(max_length=500, verbose_name=_("LinkedIn"), blank=True)
    instagram_url = models.URLField(max_length=500, verbose_name=_('Instagram'), blank=True)

    class Meta:
        verbose_name = _("People")
        verbose_name_plural = _("People")

    def __str__(self):
        return self.name
