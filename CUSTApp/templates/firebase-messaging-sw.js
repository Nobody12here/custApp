importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

firebase.initializeApp({
    apiKey: "AIzaSyBbRXoxmtNTYHHSMkUDuBAohNcNvCZWHwY",
    authDomain: "custapp-9f6b3.firebaseapp.com",
    projectId: "custapp-9f6b3",
    storageBucket: "custapp-9f6b3.firebasestorage.app",
    messagingSenderId: "514496132308",
    appId: "1:514496132308:web:be98b7af101efd773c7741"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
    console.log("Received background message ", payload);
    console.log("testing")
    const notificationTitle = payload.data?.title || "No title";
    const notificationOptions = {
        body: payload.data?.body || "No body",
        icon: '/logo.png',
        data: {
            click_action: payload.data?.click_action || '/'
        }
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    const url = event.notification.data.click_action;
    event.waitUntil(clients.openWindow(url));
});