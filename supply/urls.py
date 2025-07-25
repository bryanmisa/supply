from django.urls import path
from supply import views
from supply.views import *

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # SupplyItem URLs
    path('supplyitem/create/', views.create_supply_item, name='create_supply_item'),  # Route to the create supply item view
    path('supplyitem/lists', views.SupplyItemListView.as_view(), name='supplyitem_list'),  # Route to list supply items (if needed)
    path('supplyitem/<int:pk>/', views.SupplyItemDetailView.as_view(), name='supplyitem_detail'),  # Route to view supply item details
    path('supplyitem/<int:pk>/transaction/recieved/', views.supplyitem_transaction_receive, name='supplyitem_transaction_receive'),
    path('supplyitem/<int:pk>/transaction/deliver/', views.supplyitem_transaction_deliver, name='supplyitem_transaction_deliver'),
    
    # Supplier URLs
    path('supplier/login/', views.supplier_login, name='supplier_login'),  # Route for supplier login
    path('supplier/register/', views.supplier_registration, name='supplier_registration'),
    path('supplier/profile/<pk>/', SupplierProfileDetailView.as_view(), name='supplier_profile_detail'),
    path('supplier/choose-items/', views.supplier_choose_items, name='supplier_choose_items'),
    path('supplier/remove-items/', supplier_remove_items, name='supplier_remove_items'),

]
