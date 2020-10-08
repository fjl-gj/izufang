from _abc import get_cache_token

from django.contrib.auth import login
from django.urls import path
from rest_framework.routers import SimpleRouter

from api.views import get_province, get_district, HotCityView, get_captcha, AgentViewSet, HouseTypeViewSet, \
    EstateViewSet, TagViews, HouseInfoViewSet, get_code_by_sms, upload_photo

urlpatterns = [
    path('districts/', get_province),
    path('districts/<int:distid>/', get_district),
    path('hotcities/', HotCityView.as_view()),
    path('login/', login),
    path('captcha/', get_captcha),
    path('tel/<int:tel>/', get_code_by_sms),
    path('photos/', upload_photo),
]

router = SimpleRouter()
router.register('agents', AgentViewSet)
router.register('housetypes', HouseTypeViewSet)
router.register('estates', EstateViewSet)
router.register('tag', TagViews)
router.register('houseinfos', HouseInfoViewSet)
urlpatterns += router.urls
