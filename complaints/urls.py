from rest_framework.routers import DefaultRouter
from .views import ComplaintViewset

router = DefaultRouter()
router.register("", ComplaintViewset, basename="complaints")
urlpatterns = router.urls
