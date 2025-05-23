import django
from django.db import models
from django.db.models import Q
from django.contrib import auth
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, PermissionsMixin, AbstractBaseUser, UserManager, AbstractUser
)
from django.contrib.auth.models import Group as BaseGroup
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

if django.VERSION >= (3, 2):
    from django.contrib.auth.hashers import make_password


class CUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if django.VERSION >= (3, 2):
            user.password = make_password(password)
        else:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(
                return_tuples=True)  # pylint: disable=protected-access
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class AbstractCUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )
    username = models.CharField(
        max_length=255,
        unique=True,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        null=True,
    )
    name = models.CharField(_('name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')

    objects = CUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.name,)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class CUser(AbstractCUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Password and email are required. Other fields are optional.
    """
    class Meta(AbstractCUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def has_superuser_group(self):
        """Check if user is in the 'superuser' group."""
        return self.groups.filter(extendedgroup__for_superuser=True).exists()

    def is_effective_superuser(self):
        """User is a superuser if either the DB field is set or they belong to the 'superuser' group."""
        return self.is_superuser or self.has_superuser_group()

    def has_perm(self, perm, obj=None):
        """Grant all permissions if the user is an effective superuser."""
        return self.is_effective_superuser() or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """Grant all module permissions if the user is an effective superuser."""
        return self.is_effective_superuser() or super().has_module_perms(app_label)

class Group(BaseGroup):
    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        proxy = True


class ExtendedGroup(models.Model):
    group = models.OneToOneField(BaseGroup, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    for_superuser = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group.name} - Created on {self.date_created}"


class CustomUserManager(UserManager):

    def get_by_natural_key(self, username, email):
        return self.get(
            Q(**{self.model.USERNAME_FIELD: username}) |
            Q(**{self.model.EMAIL_FIELD: email})
        )


class StaffNotification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={
            'is_staff': True}
    )

    def __str__(self):
        return self.user.email


class BlacklistedToken(models.Model):
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token_hash
