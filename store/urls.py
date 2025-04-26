from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet, basename='customers')

urlpatterns = router.urls