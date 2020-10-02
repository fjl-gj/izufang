
from django.urls import path

from api.views import get_province, get_cityside

urlpatterns = [
    path('districts/', get_province),
    path('districts/<int:dist>/', get_cityside),
]
