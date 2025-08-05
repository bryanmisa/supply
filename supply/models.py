from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# ---------------------------------------------------------
# Custom User Model
# ---------------------------------------------------------
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('supplier', 'Supplier'),
        ('supply_manager', 'Supply Manager'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='admin')

    # Avoid reverse relation conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username



# ---------------------------------------------------------
# Supplier Profile
# ---------------------------------------------------------
class SupplierProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'user_type': 'supplier'}
    )
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)

    # New many-to-many relation to SupplyItem
    supply_items = models.ManyToManyField('SupplyItem', blank=True, related_name='suppliers')

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = 'Supplier Profile'
        verbose_name_plural = 'Supplier Profiles'

# ---------------------------------------------------------
# Supply Manager Profile
# ---------------------------------------------------------
class SupplyManagerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'user_type': 'supply_manager'}
    )
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



# ---------------------------------------------------------
# Supply Item
# ---------------------------------------------------------
class SupplyItem(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]

    item_id = models.CharField(max_length=100, unique=True)  # SKU or barcode
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    unit_of_measure = models.CharField(max_length=50)
    reorder_level = models.PositiveIntegerField(default=10)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    # Legacy FK (optional): for single-supplier linkage
    # supplier = models.ForeignKey(SupplierProfile, on_delete=models.SET_NULL, null=True, blank=True)

    # Status and additional fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    supply_image = models.ImageField(upload_to='supply_images/', blank=True, null=True)
    lead_time_days = models.PositiveIntegerField(default=7)
    expiration_date = models.DateField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Supply Item'
        verbose_name_plural = 'Supply Items'

    def __str__(self):
        return self.name

# ---------------------------------------------------------
# Supply Item Transaction
# ---------------------------------------------------------
class SupplyItemTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('received', 'Received'),
        ('issued', 'Issued'),
    ]

    supply_item = models.ForeignKey(SupplyItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    initiated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_transactions'
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transactions'
    )

    def save(self, *args, **kwargs):
        # On first save only
        if self.pk is None:
            if self.transaction_type == 'issue':
                if self.supply_item.quantity >= self.quantity:
                    self.supply_item.quantity -= self.quantity
                else:
                    raise ValueError("Insufficient stock to issue.")
            elif self.transaction_type == 'received':
                self.supply_item.quantity += self.quantity

            self.supply_item.save()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Supply Item Transaction'
        verbose_name_plural = 'Supply Item Transactions'

    def __str__(self):
        return f"{self.supply_item.name} - {self.transaction_type}" 