
from django.urls import path
from rest_framework.routers import SimpleRouter

from api.views import get_province, get_district, AgentViewSet, HouseTypeViewSet, EstateViewSet, TagViews, \
    HouseInfoViewSet, HotCityView, logo

urlpatterns = [
    path('districts/', get_province),
    path('districts/<int:distid>/', get_district),
    path('hotcities/', HotCityView.as_view()),
    path('logo/', logo)
]

router = SimpleRouter()
router.register('agents', AgentViewSet)
router.register('housetypes', HouseTypeViewSet)
router.register('estates', EstateViewSet)
router.register('tag', TagViews)
router.register('houseinfos', HouseInfoViewSet)
urlpatterns += router.urls
