from django.conf.urls import url, include
from django.contrib import admin
from .views import index
from rest_framework import routers
from booking import serializerviews as views
from .views import index, faq
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = routers.DefaultRouter()
router.register(r'places', views.PlaceViewSet)
router.register(r'buildings', views.BuildingViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name="index"),
    url(r'^user/', include('user.urls', namespace="user")),
    url(r'^booking/', include('booking.urls', namespace="booking")),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'buildings/places/(?P<id_building>\d+)/$',views.BuildingPlaceList.as_view()),
    url(r'buildings/places/unoccupied/$',views.UnoccupiedPlaceList.as_view({'post': 'list'})),
    url(r'^faq/', faq, name="faq"),
] 
