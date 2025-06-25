from CUSTApp.utils import send_sms
from CUSTApp.models import Users
user = Users.objects.get(user_id=21)

send_sms(user,"Testing ")