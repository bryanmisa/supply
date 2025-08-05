from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def add_supplier_to_group(sender, instance, created, **kwargs):
    if created and instance.user_type == 'supplier':
        supplier_group = Group.objects.get(name='Supplier')
        instance.groups.add(supplier_group)