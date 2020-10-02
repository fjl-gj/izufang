
from django.urls import path
from rest_framework.routers import SimpleRouter

from api.views import get_province, get_cityside, AgentView, HouseTypeViewSet, EstateViewSet

urlpatterns = [
    path('districts/', get_province),
    path('districts/<int:dist>/', get_cityside),
    path('agents/', AgentView.as_view()),
    path('agents/<int:pk>/', AgentView.as_view()),
]

router = SimpleRouter()
router.register('housetypes', HouseTypeViewSet)
router.register('estates', EstateViewSet)
urlpatterns += router.urls
