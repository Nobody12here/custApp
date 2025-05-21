from rest_framework.routers import DefaultRouter
from .views import RequestGuestPassView
router = DefaultRouter()
router.register(r'',RequestGuestPassView,basename='guest-pass')
urlpatterns = router.urls
