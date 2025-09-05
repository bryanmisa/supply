from django.urls import path
from supply import views
from supply.views import *

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path("logout/", views.logout_user, name="logout"),
    path("access_denied/", views.access_denied, name="access_denied"),

    # SupplyItem URLs
    path('supplyitem/create/', views.create_supply_item, name='create_supply_item'),
    path('supplyitem/lists', SupplyItemListView.as_view(), name='supplyitem_list'),
    path('supplyitem/<int:pk>/', views.SupplyItemDetailView.as_view(), name='supplyitem_detail'),
    path('supplyitem/<int:pk>/transaction/recieved/', views.supplyitem_transaction_receive, name='supplyitem_transaction_receive'),
    path('supplyitem/<int:pk>/transaction/deliver/', views.supplyitem_transaction_deliver, name='supplyitem_transaction_deliver'),
    path('supplyitem/<int:pk>/edit/', edit_supply_item, name='edit_supply_item'),
    
    # Supplier URLs
    path('supplier/login/', views.supplier_login, name='supplier_login'),
    path('supplier/register/', views.supplier_registration, name='supplier_registration'),
    path('supplier/profile/<pk>/', SupplierProfileDetailView.as_view(), name='supplier_profile_detail'),
    path('supplier/choose-items/', views.supplier_choose_items, name='supplier_choose_items'),
    path('supplier/remove-items/', supplier_remove_items, name='supplier_remove_items'),
    
    # SupplyManager URLs
    path('supplymanager/login/', views.supply_manager_login, name='supplymanager_login'),
    path('supply_manager/profile/update/', update_supply_manager_profile, name='update_supply_manager_profile'),
    path('supplymanager/register/', views.supply_manager_registration, name='supplymanager_registration'),
    #path('supply_manager/profile/', supply_manager_profile_detail, name='supply_manager_profile_detail'),
    path('supplymanager/profile/<pk>/', SupplyManagerProfileDetailView.as_view(), name='supplymanager_profile_detail'),
    
    # Customer URLS
     path('customer/login/', views.customer_login, name='customer_login'),
     path('customer/register/', views.customer_registration, name='customer_registration'),
     path('requestable-supply/', views.customer_requestable_supply, name='customer_requestable_supply'),
     path('request-supply/<int:item_id>/', views.request_supply_item, name='request_supply_item'),

]
