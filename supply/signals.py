from datetime import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from supply.models import *

@receiver(post_save, sender=CustomUser)
def add_supplier_to_group(sender, instance, created, **kwargs):
    if created and instance.user_type == 'supplier':
        supplier_group = Group.objects.get(name='Supplier')
        instance.groups.add(supplier_group)

@receiver(post_save, sender=CustomUser)
def create_supplier_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'supplier':
        SupplierProfile.objects.create(user=instance)
        

@receiver(post_save, sender=SupplyItemRequest)
def handle_supply_request(sender, instance, created, **kwargs):
    if created:
        # Update the supply item quantity
        supply_item = instance.supply_item
        requested_quantity = instance.quantity
        
        # Create a new supply transaction
        SupplyItemTransaction.objects.create(
            supply_item=supply_item,
            customer=instance.customer,
            quantity=requested_quantity,
            transaction_type='REQUEST',
            status='NEW',
            transaction_date=timezone.now()
        )
        
        # Update the available quantity
        supply_item.quantity -= requested_quantity
        supply_item.save()
        
