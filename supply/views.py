from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required

from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy

from supply.forms import (
    SupplyItemForm,
    SupplierProfileForm,
    SupplierSupplyItemsForm,
    SupplierLoginForm,
    SupplyItemTransactionForm,
    UserProfileForm,
    SupplyManagerProfileForm,
    SupplyManagerLoginForm,
    CustomerProfileForm,
    CustomerLoginForm
)
from supply.models import (
    SupplyItem, 
    SupplierProfile, 
    SupplyManagerProfile, 
    SupplyItemRequest, 
    SupplyItemTransaction,
    )

#region Permissions

def is_supply_manager(user):
    return user.is_authenticated and user.user_type == 'supply_manager'

def is_supplier(user):
    return user.is_authenticated and user.user_type == 'supplier'

def is_customer(user):
    return user.is_authenticated and user.user_type == 'customer'

def handle_permission_denied(request):
    messages.error(request, "You don't have permission to access this page.")
    if request.user.is_authenticated:
        if request.user.user_type == 'supplier':
            return redirect('supplier_choose_items')
        elif request.user.user_type == 'customer':
            return redirect('customer_requestable_supply')
        elif request.user.user_type == 'supply_manager':
            return redirect('supplyitem_list')
    return redirect('access_denied')

#endregion Permissions

#region HomePage, DashBoard, Logout
def dashboard(request):
    """
    Render the dashboard views
    """
    return render(request, 'supply/supplyitem_create.html')

def home_page(request):
    return render(request, 'home/index.html')

def logout_user(request):
    logout(request)
    storage = messages.get_messages(request)
    storage.used = True  # Clears all queued messages   
    return redirect('home_page') 

def access_denied(request):
    return render(request, 'errors/access_denied.html')

#endregion HomePage, DashBoard, Logout

#region SupplyItem Views


@user_passes_test(is_supply_manager)
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


# For Supply Items
class SupplyItemListView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, ListView):
    permission_required = 'supply.view_supplyitem'
    model = SupplyItem
    template_name = 'supply/supplyitem_list.html'
    context_object_name = 'supply_items'

    def test_func(self):
        return self.request.user.user_type == 'supply_manager'

    def handle_no_permission(self):
        return handle_permission_denied(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = {item.id: SupplyItemForm(instance=item) for item in self.get_queryset()}
        return context

class SupplyItemDetailView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'supply.view_supplyitem'
    model = SupplyItem
    template_name = 'supply/supplyitem_detail.html'
    context_object_name = 'supply_item'

    def test_func(self):
        return self.request.user.user_type == 'supply_manager'

    def handle_no_permission(self):
        return handle_permission_denied(self.request)

@user_passes_test(is_supply_manager)
def edit_supply_item(request, pk):
    item = get_object_or_404(SupplyItem, pk=pk)
    if request.method == 'POST':
        form = SupplyItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Supply item updated successfully!")
            return redirect('supplyitem_list')
    else:
        form = SupplyItemForm(instance=item)
    return render(request, 'supply/supplyitem_edit.html', {'form': form, 'item': item})

#endregion SupplyItem Views   

#region Supplier Views
#@permission_required('supply.add_supplierprofile', raise_exception=True)
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
        form = SupplierLoginForm(request.POST)  # Ensure you are using the correct form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.user_type == 'supplier':
                    try:
                        # Check if the SupplierProfile exists
                        supplier_profile = user.supplierprofile
                    except ObjectDoesNotExist:
                        messages.error(request, "Your profile is incomplete. Please contact support.")
                        return redirect('supplier_registration')  # Redirect to registration or profile creation page

                    login(request, user)
                    return redirect('supplier_choose_items')  # Redirect to the supplier dashboard
                else:
                    messages.error(request, "You are not authorized to log in as a supplier.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = SupplierLoginForm()  # Initialize an empty form for GET requests
    return render(request, 'supplier/supplier_login.html', {'form': form})

# For Supplier Profile
class SupplierProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'supply.view_supplierprofile'
    model = SupplierProfile
    template_name = 'supplier/supplier_profile_detail.html'
    context_object_name = 'supplier'

    def test_func(self):
        return self.request.user.user_type == 'supplier'

    def handle_no_permission(self):
        return handle_permission_denied(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        context['supply_items'] = supplier.supply_items.all()
        return context

@login_required
@user_passes_test(is_supplier)
#@permission_required('supply.change_supplierprofile', raise_exception=True)
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
    
class SupplyItemTransactionListView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, ListView):
    permission_required = 'supply.view_supplyitemtransaction'
    model = SupplyItemTransaction
    template_name = 'supply/supplyitem_transaction.html'
    context_object_name = 'transactions'
    paginate_by = 10 #Add this line to limit to 5 items per page
    def test_func(self):
        return self.request.user.user_type == 'supply_manager'

    def handle_no_permission(self):
        return handle_permission_denied(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = {item.id: SupplyItemTransactionForm(instance=item) for item in self.get_queryset()}
        return context

#endregion SupplyItemTransaction Views

#region Supply Manager Views

def supply_manager_login(request):
    template_name = 'supply_manager/supply_manager_login.html'
    success_url = reverse_lazy('supply:supplyitem_list')

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
                return redirect(success_url)
            else:
                messages.error(request, f"User '{user.username}' is not authorized as a Supply Manager.")
                return redirect(reverse_lazy('supply:supplymanager_login'))
        else:
            messages.error(request, "Invalid username or password.")
            return redirect(reverse_lazy('supply:supplymanager_login'))
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

@login_required
def update_supply_manager_profile(request):
    try:
        profile = request.user.supplymanagerprofile
    except SupplyManagerProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = SupplyManagerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            supply_manager_profile = form.save(commit=False)
            supply_manager_profile.user = request.user
            supply_manager_profile.save()
            return redirect('supply_manager_profile_detail')  # Redirect to the profile detail page
    else:
        form = SupplyManagerProfileForm(instance=profile)

    return render(request, 'supply_manager/update_supply_manager_profile.html', {'form': form})

class SupplyManagerProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = SupplyManagerProfile
    template_name = 'supply_manager/supply_manager_profile_detail.html'
    context_object_name = 'profile'

    def test_func(self):
        return self.request.user.user_type == 'supply_manager'

    def handle_no_permission(self):
        return handle_permission_denied(self.request)

    def get_object(self, queryset=None):
        return self.request.user.supplymanagerprofile

class SupplyManagerProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SupplyManagerProfile
    form_class = SupplyManagerProfileForm
    template_name = 'supply_manager/update_supply_manager_profile.html'
    success_url = reverse_lazy('supply_manager_profile_detail')

    def test_func(self):
        return self.request.user.user_type == 'supply_manager'

    def handle_no_permission(self):
        return handle_permission_denied(self.request)

    def get_object(self, queryset=None):
        return self.request.user.supplymanagerprofile

@login_required
@user_passes_test(is_supply_manager)
def approve_request(request, pk):
    """Approve a supply request and update transaction"""
    supply_request = get_object_or_404(SupplyItemRequest, pk=pk)
    
    if supply_request.status != 'PENDING':
        messages.error(request, "This request cannot be approved because it's not in pending status.")
        return redirect('supply:customer_pending_requests')
    
    try:
        # Update the request status
        supply_request.status = 'APPROVED'
        supply_request.save()
        
        # Update or create the corresponding transaction
        transaction = SupplyItemTransaction.objects.get(
            supply_item=supply_request.supply_item,
            customer=supply_request.customer,
            transaction_type='REQUEST'
        )
        transaction.status = 'PROCESSING'
        transaction.save()
        
        messages.success(request, f"Request for {supply_request.supply_item.name} has been approved.")
    except Exception as e:
        messages.error(request, f"Error processing approval: {str(e)}")
    
    return redirect('supply:customer_pending_requests')

@login_required
@user_passes_test(is_supply_manager)
def reject_request(request, pk):
    """Reject a supply request and update transaction"""
    supply_request = get_object_or_404(SupplyItemRequest, pk=pk)
    
    if supply_request.status != 'PENDING':
        messages.error(request, "This request cannot be rejected because it's not in pending status.")
        return redirect('supply:customer_pending_requests')
    
    try:
        # Update the request status
        supply_request.status = 'REJECTED'
        supply_request.save()
        
        # Update the corresponding transaction
        transaction = SupplyItemTransaction.objects.get(
            supply_item=supply_request.supply_item,
            customer=supply_request.customer,
            transaction_type='REQUEST'
        )
        transaction.status = 'CANCELLED'
        transaction.save()
        
        # Return the quantity back to supply item
        supply_item = supply_request.supply_item
        supply_item.quantity += supply_request.quantity
        supply_item.save()
        
        messages.success(request, f"Request for {supply_request.supply_item.name} has been rejected.")
    except Exception as e:
        messages.error(request, f"Error processing rejection: {str(e)}")
    
    return redirect('supply:customer_pending_requests')

@login_required
@user_passes_test(is_supply_manager)
def complete_transaction(request, pk):
    """Mark a transaction as completed after delivery"""
    transaction = get_object_or_404(SupplyItemTransaction, pk=pk)
    
    if transaction.status != 'PROCESSING':
        messages.error(request, "This transaction cannot be completed because it's not in processing status.")
        return redirect('transaction_list')
    
    try:
        transaction.status = 'COMPLETED'
        transaction.save()
        
        messages.success(request, f"Transaction for {transaction.supply_item.name} has been completed.")
    except Exception as e:
        messages.error(request, f"Error completing transaction: {str(e)}")
    
    return redirect('transaction_list')
#endregion Supply Manager Views

# ---------------------
#region Customer Views
# ---------------------
def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)  # Ensure you have this form in forms.py
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.user_type == 'customer':
                    try:
                        # Check if the CustomerProfile exists
                        customer_profile = user.customerprofile
                    except ObjectDoesNotExist:
                        messages.error(request, "Your profile is incomplete. Please contact support.")
                        return redirect('customer_registration')

                    login(request, user)
                    return redirect('customer_requestable_supply')
                else:
                    messages.error(request, "You are not authorized to log in as a customer.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomerLoginForm()  # Initialize an empty form for GET requests
    
    return render(request, 'customer/customer_login.html', {'form': form})

def customer_registration(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST)
        customer_form = CustomerProfileForm(request.POST)
        
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = 'customer'
            user.save()
            
            customer_profile = customer_form.save(commit=False)
            customer_profile.user = user
            customer_profile.save()
            
            messages.success(request, "Registration successful. Please login.")
            return redirect('customer_login')
    else:
        user_form = UserProfileForm()
        customer_form = CustomerProfileForm()
        
    return render(request, 'customer/customer_registration.html', {
        'user_form': user_form, 
        'customer_form': customer_form
    })

#endregion Customer Views

# ------------------------------------
#region Customer Supply Request Views
# -----------------------------------

@login_required
@user_passes_test(is_customer)
def customer_requestable_supply(request):
    supply_items = SupplyItem.objects.filter(status='active').prefetch_related('suppliers')
    return render(request, 'customer/customer_requestable_supply.html', {
        'supply_items': supply_items
    })


@login_required
@user_passes_test(is_customer)
def request_supply_item(request, item_id):
    if request.method == 'POST':
        supply_item = get_object_or_404(SupplyItem, id=item_id)
        requested_quantity = int(request.POST.get('quantity', 0))

        
        # Validate quantity
        if requested_quantity <= 0:
            messages.error(request, "Please enter a valid quantity.")
            return redirect('customer_requestable_supply')
            
        if requested_quantity > supply_item.quantity:
            messages.error(request, "Requested quantity exceeds available stock.")
            return redirect('customer_requestable_supply')
            
        # Create the supply request
        SupplyItemRequest.objects.create(
            supply_item=supply_item,
            customer=request.user.customerprofile,
            quantity=requested_quantity,

        )
        
        messages.success(request, "Supply request submitted successfully.")
        return redirect('customer_requestable_supply')
        
    return redirect('customer_requestable_supply')

class CustomerSupplyRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = SupplyItemRequest
    template_name = 'customer/customer_supply_request/customer_supply_request.html'
    context_object_name = 'supply_requests'
    
    def test_func(self):
        return self.request.user.user_type == 'customer'
    
    def get_queryset(self):
        return SupplyItemRequest.objects.filter(
            customer=self.request.user.customerprofile
        ).order_by('-request_date')

class CustomerPendingRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = SupplyItemRequest
    template_name = 'supply_manager/customer_related/pending_customer_request.html'
    context_object_name = 'pending_requests'
    
    def test_func(self):
        return self.request.user.user_type == 'supply_manager'
    
    def get_queryset(self):
        return SupplyItemRequest.objects.filter(
            status='PENDING'
        ).order_by('-request_date')
#endregion Customer Views