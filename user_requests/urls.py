from rest_framework.routers import DefaultRouter
from .views import RequestViewset

router = DefaultRouter()
router.register("", RequestViewset, basename="application-requests")
urlpatterns = router.urls
