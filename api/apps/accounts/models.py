from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from api.utils.db.models import UUIDPrimaryKeyMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """
        Creates a custom user with the given fields
        """
        user = self.model(email=self.normalize_email(email), **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs['is_superuser'] = True
        user = self.create_user(email, password=password, **kwargs)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, UUIDPrimaryKeyMixin, PermissionsMixin):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField('Primary Email', max_length=100, unique=True, null=False, blank=False)

    first_name = models.CharField(max_length=128)

    last_name = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)

    created_on = CreationDateTimeField()

    updated_at = ModificationDateTimeField()

    objects = UserManager()

    class Meta:
        db_table = 'users'
        default_related_name = 'users'
        ordering = ['email']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser
