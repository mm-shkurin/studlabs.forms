from django.urls import path
from .views import*

urlpatterns = [
    path('', FormCreateView.as_view(), name='form-create'),
    path('list/', FormListView.as_view(), name='form-list'),
    path('<str:pk>/', FormDetailView.as_view(), name='form-detail'),
    path('<str:form_id>/responses/', ResponseCreateView.as_view(), name='response-create'),
    path('<str:id>/stats/', FormStatsView.as_view(), name='form-stats'),
]