"""
sentry.models.user
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from sentry.db.models import Model
from sentry.manager import UserManager


class User(Model, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=128, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager(cache_fields=['pk'])

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'sentry'
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.first_name

    def get_short_name(self):
        return self.username

    def merge_to(from_user, to_user):
        # TODO: we could discover relations automatically and make this useful
        from sentry.models import (
            GroupBookmark, Project, ProjectKey, Team, TeamMember, UserOption)

        for obj in ProjectKey.objects.filter(user=from_user):
            obj.update(user=to_user)
        for obj in TeamMember.objects.filter(user=from_user):
            obj.update(user=to_user)
        for obj in Project.objects.filter(owner=from_user):
            obj.update(owner=to_user)
        for obj in Team.objects.filter(owner=from_user):
            obj.update(owner=to_user)
        for obj in GroupBookmark.objects.filter(user=from_user):
            obj.update(user=to_user)
        for obj in UserOption.objects.filter(user=from_user):
            obj.update(user=to_user)