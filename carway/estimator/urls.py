from django.urls import path
from . import views

urlpatterns = [
    path('', views.estimator_home, name='estimator-home'),
    path('manage/', views.manage_models, name='manage-models'),
    path('train/', views.train_new_model, name='train-model'),
    path('set-active/<int:model_id>/', views.set_active_model, name='set-active-model'),
    path('delete/<int:model_id>/', views.delete_model, name='delete-model'),
]