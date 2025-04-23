from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListingListView.as_view(), name='listing-list'),
    path('new/', views.ListingCreateView.as_view(), name='listing-create'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/update/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing-delete'),
    path('search/', views.search_listings, name='search-listings'),
    path('user/<str:username>', views.UserListingListView.as_view(), name='user-listings'),
    path('ajax/load-models/', views.load_models, name='ajax-load-models'),
]
