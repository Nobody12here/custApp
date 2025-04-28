const registerSw = async ()=>{
    if('serviceWorker' in navigator){
        const reg = await navigator.serviceWorker.register('/sw.js');
        initialiseState(reg)
    } 
    else {
        console.error("You cannot send push notifications")
    }
}
const initialiseState = (reg) => {
    if (!reg.showNotification) {
        console.error('Showing notifications isn\'t supported ☹️😢');
        return
    }
    if (Notification.permission === 'denied') {
        console.error('You prevented us from showing notifications ☹️🤔');
        return
    }
    if (!'PushManager' in window) {
        console.error("Push isn't allowed in your browser 🤔");
        return
    }
    
    subscribe(reg);
}   
function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));

    return outputData;
}

const subscribe = async (reg) => {
    const subscription = await reg.pushManager.getSubscription();
    if (subscription) {
        sendSubData(subscription);
        return;
    }

    const vapidMeta = document.querySelector('meta[name="vapid-key"]');
    const key = "BEUPeYWttrMsi5a56-vp9nmIDAJ6kReVWyvsGbLVmJAoRJABTAM20xC2qnlPCPlre_uebZYKTEMbOaFmfqrRk9s"
    const options = {
        userVisibleOnly: true,
        // if key exists, create applicationServerKey property
        ...(key && {applicationServerKey: urlB64ToUint8Array(key)})
    };

    const sub = await reg.pushManager.subscribe(options);
    sendSubData(sub)
};
const sendSubData = async (subscription) => {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: 'subscribe',
        subscription: subscription.toJSON(),
        browser: browser,
    };
    const token = localStorage.getItem('access_token'); // Make sure the token is stored here after login
    if (!token) {
        console.error('No JWT token found.');
        return;
    }

    const res = await fetch('/webpush/save_information', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        credentials: "include"
    });

    handleResponse(res);
};

const handleResponse = (res) => {
    console.log(res.status);
};

registerSw();