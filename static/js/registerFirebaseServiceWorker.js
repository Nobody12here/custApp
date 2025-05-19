import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import {
  getMessaging,
  getToken,
  onMessage,
} from "https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js";

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyBbRXoxmtNTYHHSMkUDuBAohNcNvCZWHwY",
  authDomain: "custapp-9f6b3.firebaseapp.com",
  projectId: "custapp-9f6b3",
  storageBucket: "custapp-9f6b3.firebasestorage.app",
  messagingSenderId: "514496132308",
  appId: "1:514496132308:web:be98b7af101efd773c7741"
};

// ✅ Use v9 modular syntax
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// Ask for notification permission
Notification.requestPermission().then((permission) => {
  if (permission === "granted") {
    getToken(messaging, {
      vapidKey: "BKBhMjA_enYthg33S8dp3gHCsmdmBpn6eYuKrWzRcqdP8pP45SHb64wd2wnBeNkYYaJhnwVSo8kb4_09KLOxtPs",
    }).then((currentToken) => {
      if (currentToken) {
        console.log("FCM Token:", currentToken);

        const access_token = localStorage.getItem('access_token');
        fetch("/devices/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${access_token}`,
          },
          body: JSON.stringify({
            registration_id: currentToken,
            type: "web",
          }),
        });
      } else {
        console.log("No registration token available.");
      }
    }).catch((err) => {
      console.log("An error occurred while retrieving token. ", err);
    });
  } else {
    console.log("Notification permission not granted.");
  }
});

// Handle foreground messages
onMessage(messaging, (payload) => {
  console.log("Message received. ", payload);
  // alert(`${payload.notification?.title || "No title"}\n${payload.notification?.body || "No body"}`);
});
