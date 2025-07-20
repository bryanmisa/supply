from django import forms
from supply.models import SupplyItem, SupplierProfile, CustomUser

class SupplyItemForm(forms.ModelForm):
    class Meta:
        model = SupplyItem
        fields = [
            'item_id',
            'name',
            'description',
            'category',
            'unit_of_measure',
            'reorder_level',
            'unit_cost',
            'supplier',
            'status',
            'supply_image',
            'lead_time_days',
            'expiration_date',
        ]
        widgets = {
            'item_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit of Measure'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Reorder Level'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Unit Cost'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'supply_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'lead_time_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Lead Time (days)'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password' ,'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }
        
class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = ['company_name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
        }
