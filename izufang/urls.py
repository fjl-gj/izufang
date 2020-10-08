"""izufang URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.conf.urls.static import static
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from common.views import show_index
from izufang import settings

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='项目接口文档')

urlpatterns = [
    path('', show_index),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/docs/', schema_view),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
