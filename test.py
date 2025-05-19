#For testing stuff

from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize the app with your service account
if not firebase_admin._apps:
    cred = credentials.Certificate("./project/firebase/key.json")
    firebase_admin.initialize_app(cred)
message = messaging.Message(
    data={
        "title": "Hello",
        "body": "World",
        "click_action": "/some-url"
    },
    token="dORzaTEeV6TWkATZpdQOi4:APA91bFtI53cTA4YcIHXgaaEHGZL14y6-X3x4aTSutWS9kyoVH2-x6XeNJ1hNIEb7MS3XwnVJ4GG3-DPft-2b2l3blcyNaSu2zK_yUJk9yTHRe5l-kxz-eg"
)

response = messaging.send(message)
print("Sent message:", response)