from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

from store.models import Customer
from ..models import ExtendedGroup
from dotenv import load_dotenv

load_dotenv()

admin_group_name = 'Primary Administrator'

@receiver(post_migrate)
def create_superuser_group(sender, **kwargs):
    """Ensure the 'superuser' group exists after migrations."""
    Group.objects.get_or_create(name=admin_group_name)

@receiver(post_save, sender=Group)
def create_extended_group(sender, instance, **kwargs):
    if kwargs['created']:
        for_superuser = instance.name == admin_group_name
        ExtendedGroup.objects.create(group=instance, for_superuser=for_superuser)


@receiver(post_delete, sender=Customer)
def delete_associated_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()




