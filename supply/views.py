from django.shortcuts import render, redirect, get_object_or_404
from supply.forms import SupplyItemForm, SupplierProfileForm, UserProfileForm
from supply.models import SupplyItem
from django.views.generic import ListView, DetailView

# Create your views here.
def dashboard(request):
    """Render the dashboard views
    """
    return render(request, 'supply/supplyitem_create.html')


def create_supply_item(request):
    if request.method == 'POST':
        form = SupplyItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplyitem_list')  # replace with your success URL
    else:
        form = SupplyItemForm()
    return render(request, 'supply/supplyitem_create.html', {'form': form})


class SupplyItemListView(ListView):
    model = SupplyItem
    template_name = 'supply/supplyitem_list.html'
    context_object_name = 'supply_items'

class SupplyItemDetailView(DetailView):
    model = SupplyItem
    template_name = 'supply/supplyitem_detail.html'
    context_object_name = 'supply_item' 
    

def supplier_registration(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST)
        supplier_form = SupplierProfileForm(request.POST)
        
        if user_form.is_valid() and supplier_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = 'supplier'
            user.save()
            
            supplier_profile = supplier_form.save(commit=False)
            supplier_profile.user = user
            supplier_profile.save()
            return redirect('supplyitem_list')  # Redirect to a success page
        
    else:
        user_form = UserProfileForm()
        supplier_form = SupplierProfileForm()
        
    return render(request, 'supplier/supplier_registration.html', {'user_form': user_form, 'supplier_form': supplier_form})

