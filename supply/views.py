from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from supply.forms import *
from supply.models import SupplyItem
from django.views.generic import ListView, DetailView

# Create your views here.
def dashboard(request):
    """Render the dashboard views
    """
    return render(request, 'supply/supplyitem_create.html')

#region SupplyItem Views
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

#endregion SupplyItem Views   


#region Supplier Views
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

#endregion Supplier Views


#region SupplyItemTransaction Views

def supplyitem_transaction_issue(request, pk):
    supply_item = get_object_or_404(SupplyItem, pk=pk)
    
    if request.method == 'POST':
        form = SupplyItemTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.supply_item = supply_item
            transaction.transaction_type = 'issue'
            transaction.transaction_date = datetime.now()
            transaction.initiated_by = request.user  # uses `related_name='initiated_transactions'
            transaction.save()
            supply_item.update_quantity()

            return redirect('supplyitem_detail', pk=supply_item.pk)
    else:
        form = SupplyItemTransactionForm()

    return render(request, 'supply/supplyitem_transaction.html', {
        'form': form,
        'supply_item': supply_item
    })
 

def supplyitem_transaction_received(request, pk):
    supply_item = get_object_or_404(SupplyItem, pk=pk)
    
    if request.method == 'POST':
        form = SupplyItemTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.supply_item = supply_item
            transaction.transaction_type = 'received'
            transaction.transaction_date = datetime.now()
            transaction.initiated_by = request.user  # uses `related_name='initiated_transactions'`
            transaction.save()

            return redirect('supplyitem_detail', pk=supply_item.pk)
    else:
        form = SupplyItemTransactionForm()

    return render(request, 'supply/supplyitem_transaction.html', {
        'form': form,
        'supply_item': supply_item
    })
    
#endregion SupplyItemTransaction Views