const tg = window.Telegram.WebApp;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const sendBtn = document.getElementById('send-btn');
const retryBtn = document.getElementById('retry-btn');

tg.expand();
tg.ready();

// Start camera
async function initCamera() {
    const constraints = [
        { video: { facingMode: 'user' }, audio: false },
        { video: true, audio: false }
    ];

    for (const constraint of constraints) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraint);
            video.srcObject = stream;
            video.onloadedmetadata = () => {
                video.play();
            };
            return;
        } catch (err) {
            console.error("Constraint failed:", constraint, err);
        }
    }

    alert("Kameraga ruxsat berilmadi yoki u ishlamayapti. Iltimos, brauzer sozlamalarini tekshiring.");
}

initCamera();

captureBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Mirror the image for the canvas
    context.translate(canvas.width, 0);
    context.scale(-1, 1);

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const capturedImage = canvas.toDataURL('image/png');

    // Send immediately to bot
    tg.sendData(capturedImage);

    // Show loading or localized feedback
    captureBtn.innerText = "Yuborilmoqda... ✅";
    captureBtn.disabled = true;
});
