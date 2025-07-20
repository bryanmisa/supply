from django.contrib import admin
from supply.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(SupplierProfile)
admin.site.register(SupplyItem)
