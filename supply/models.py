from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# ---------------------------------------------------------
#region Custom User Model
# ---------------------------------------------------------
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('supplier', 'Supplier'),
        ('supply_manager', 'Supply Manager'),
        ('customer', 'Customer'),
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
#region Supplier Profile
# ---------------------------------------------------------
class SupplierProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'supplier'}, default=None
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
#region Supply Manager Profile
# ---------------------------------------------------------
class SupplyManagerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'supply_manager'},  default=None
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    employee_id = models.CharField(max_length=50,)
    is_active = models.BooleanField(default=True)
    
    
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'}, default=None)
    address = models.TextField()
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# ---------------------------------------------------------
#region Supply Item
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
#region Supply Item Transaction
# ---------------------------------------------------------
class SupplyItemTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('REQUESTED', 'Requested'),   # requested by customer
        ('DELIVERY', 'Delivery'), # delivery from supplier to supply manager
        ('RETURN', 'Return')      # returned by customer to supply manager or supply manager to supplier
    ]
    
    TRANSACTION_STATUS = [
        ('NEW', 'New Request'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    supply_item = models.ForeignKey(SupplyItem, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE,  default=None, null=True)
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='NEW')
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.supply_item.name}" 


# ---------------------------------------------------------
#region Supply Item Requests
# ---------------------------------------------------------
class SupplyItemRequest(models.Model):
    supply_item = models.ForeignKey(SupplyItem, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, default=None, null=True)
    quantity = models.PositiveIntegerField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('FOR DELIVERY', 'For Delivery'),
            ('FOR RETURN', 'For Return'),
            ('COMPLETED', 'Completed'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING'
    )

    def __str__(self):
        return f"Request for {self.supply_item.name} by {self.customer.user.username}"