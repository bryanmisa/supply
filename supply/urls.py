from django.urls import path
from supply import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('supplier/register/', views.supplier_registration, name='supplier_registration'),
    path('supplyitem/create/', views.create_supply_item, name='create_supply_item'),  # Route to the create supply item view
    path('supplyitem/lists', views.SupplyItemListView.as_view(), name='supplyitem_list'),  # Route to list supply items (if needed)
    path('supplyitem/<int:pk>/', views.SupplyItemDetailView.as_view(), name='supplyitem_detail'),  # Route to view supply item details

]
