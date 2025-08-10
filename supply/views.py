
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages

from django.views.generic import ListView, DetailView, CreateView

from django.urls import reverse_lazy

from supply.forms import *
from supply.models import SupplyItem



# Create your views here.
def dashboard(request):
    """Render the dashboard views
    """
    return render(request, 'supply/supplyitem_create.html')

def home_page(request):
    return render(request, 'home/index.html')


def logout_user(request):
    logout(request)
    return redirect(reverse_lazy('home_page'))

#region SupplyItem Views
from django.contrib.auth.decorators import permission_required

@permission_required('supply.add_supplyitem', raise_exception=True)
def create_supply_item(request):
    if request.method == 'POST':
        form = SupplyItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplyitem_list')  # replace with your success URL
    else:
        form = SupplyItemForm()
    return render(request, 'supply/supplyitem_create.html', {'form': form})


from django.contrib.auth.mixins import PermissionRequiredMixin

class SupplyItemListView(PermissionRequiredMixin, ListView):
    permission_required = 'supply.view_supplyitem'
    model = SupplyItem
    template_name = 'supply/supplyitem_list.html'
    context_object_name = 'supply_items'

class SupplyItemDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'supply.view_supplyitem'
    model = SupplyItem
    template_name = 'supply/supplyitem_detail.html'
    context_object_name = 'supply_item' 
#endregion SupplyItem Views   


#region Supplier Views
@permission_required('supply.add_supplierprofile', raise_exception=True)
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

def supplier_login(request):
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('supplier_profile_detail', pk=user.supplierprofile.pk)  # Redirect to supplier profile
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = SupplierLoginForm()
    return render(request, 'supplier/supplier_login.html', {'form': form})

class SupplierProfileDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'supply.can_view_supplier_profile'
    model = SupplierProfile
    template_name = 'supplier/supplier_profile_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Explicitly load supply_items to ensure availability
        supplier = self.object
        context['supply_items'] = supplier.supply_items.all()

        return context

@permission_required('supply.change_supplierprofile', raise_exception=True)
def supplier_choose_items(request):
    supplier_profile = get_object_or_404(SupplierProfile, user=request.user)

    # Get IDs of already selected items
    selected_items = supplier_profile.supply_items.values_list('id', flat=True)

    if request.method == 'POST':
        form = SupplierSupplyItemsForm(request.POST, instance=supplier_profile)
        # Show only items not already selected
        form.fields['supply_items'].queryset = SupplyItem.objects.exclude(id__in=selected_items)

        if form.is_valid():
            # Get new items selected from the form
            new_items = form.cleaned_data['supply_items']

            # Add them to the existing set instead of replacing
            supplier_profile.supply_items.add(*new_items)

            return redirect('supplier_profile_detail', pk=supplier_profile.pk)
    else:
        form = SupplierSupplyItemsForm(instance=supplier_profile)
        # Show only items not already selected
        form.fields['supply_items'].queryset = SupplyItem.objects.exclude(id__in=selected_items)

    return render(
        request,
        'supplier/supplier_choose_items.html',
        {'form': form, 'supplier': supplier_profile}
    )
    
@permission_required('supply.change_supplierprofile', raise_exception=True)
def supplier_remove_items(request):
    supplier_profile = get_object_or_404(SupplierProfile, user=request.user)

    # Get all currently assigned items
    current_items = supplier_profile.supply_items.all()

    if request.method == 'POST':
        # Get selected items to remove (IDs passed from checkboxes)
        items_to_remove = request.POST.getlist('remove_items')
        supplier_profile.supply_items.remove(*items_to_remove)  # Remove them

        return redirect('supplier_profile_detail', pk=supplier_profile.pk)

    return render(
        request,
        'supplier/supplier_remove_items.html',
        {
            'supplier': supplier_profile,
            'current_items': current_items
        }
    )
#endregion SupplierViews

#region SupplyItemTransaction Views

@permission_required('supply.add_supplyitemtransaction', raise_exception=True)
def supplyitem_transaction_deliver(request, pk):
    supply_item = get_object_or_404(SupplyItem, pk=pk)
    
    if request.method == 'POST':
        form = SupplyItemTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.supply_item = supply_item
            transaction.transaction_type = 'issue'
            transaction.transaction_date = datetime.now()
            transaction.initiated_by = request.user  # uses `related_name='initiated_transactions'`
            # The quantity is already set by the form, and the model's save() method handles the update
            transaction.save()

            return redirect('supplyitem_detail', pk=supply_item.pk)
    else:
        form = SupplyItemTransactionForm()

    return render(request, 'supply/supplyitem_transaction.html', {
        'form': form,
        'supply_item': supply_item
    })
 

@permission_required('supply.add_supplyitemtransaction', raise_exception=True)
def supplyitem_transaction_receive(request, pk):
    supply_item = get_object_or_404(SupplyItem, pk=pk)
    
    if request.method == 'POST':
        form = SupplyItemTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.supply_item = supply_item
            transaction.transaction_type = 'received'
            transaction.transaction_date = datetime.now()
            transaction.initiated_by = request.user  # uses `related_name='initiated_transactions'`
            # The quantity is already set by the form, so we just need to save
            transaction.save()

            return redirect('supplyitem_detail', pk=supply_item.pk)
    else:
        form = SupplyItemTransactionForm()

    return render(request, 'supply/supplyitem_transaction.html', {
        'form': form,
        'supply_item': supply_item
    })
    
#endregion SupplyItemTransaction Views

#region Supply Manager Views

def supply_manager_login(request):
    template_name = 'supply_manager/supply_manager_login.html'
    success_url = reverse_lazy('supplyitem_list')

    # Redirect authenticated user
    if request.user.is_authenticated:
        return redirect(success_url)

    if request.method == 'POST':
        form = SupplyManagerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

        if user is not None:
            if getattr(user, 'user_type', '') == 'supply_manager':
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! You are now logged in as Supply Manager.")
                return redirect(success_url)
            else:
                messages.error(request, f"User '{user.username}' is not authorized as a Supply Manager.")
                return redirect(reverse_lazy('supplymanager_login'))
        else:
            messages.error(request, "Invalid username or password.")
            return redirect(reverse_lazy('supplymanager_login'))
    else:
        form = SupplyManagerLoginForm()

    context = {
        'form': form,
        'title': 'Supply Manager Login',
    }
    
    return render(request, template_name, context)



#@permission_required('supply.add_supplymanagerprofile', raise_exception=True)
def supply_manager_registration(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST)
        supply_manager_form = SupplyManagerProfileForm(request.POST)
        
        if user_form.is_valid() and supply_manager_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = 'supply_manager'
            user.save()
            
            supply_manager_profile = supply_manager_form.save(commit=False)
            supply_manager_profile.user = user
            supply_manager_profile.save()
            return redirect('supplyitem_list')  # Redirect to a success page
        
    else:
        user_form = UserProfileForm()
        supply_manager_form = SupplyManagerProfileForm()
        
    return render(request, 'supply_manager/supply_manager_registration.html', {'user_form': user_form, 'supply_manager_form': supply_manager_form})
#endregion Supply Manager Views