from CUSTApp.utils import notify_user_devices
from CUSTApp.models import Users
user = Users.objects.get(uu_id="AAF223017")

notify_user_devices(user,"Testing ", "This is a test notification")