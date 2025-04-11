from rest_framework.routers import DefaultRouter
from .views import ApplicationTemplateViewset

router = DefaultRouter()
router.register(r'', ApplicationTemplateViewset)

urlpatterns = router.urls