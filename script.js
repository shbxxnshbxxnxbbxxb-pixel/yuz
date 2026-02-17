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
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'user',
                width: { ideal: 1280 },
                height: { ideal: 1280 }
            },
            audio: false
        });
        video.srcObject = stream;
    } catch (err) {
        console.error("Camera error:", err);
        alert("Kameraga ruxsat berilmadi yoki u ishlamayapti.");
    }
}

initCamera();

let capturedImage = null;

captureBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Mirror the image for the canvas too
    context.translate(canvas.width, 0);
    context.scale(-1, 1);

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    capturedImage = canvas.toDataURL('image/png');

    video.style.display = 'none';
    canvas.style.display = 'block';
    // Remove the mirror transform for display if needed, but easier to keep it simple
    canvas.style.width = '100%';
    canvas.style.borderRadius = '50%';

    captureBtn.style.display = 'none';
    sendBtn.style.display = 'block';
    retryBtn.style.display = 'block';
});

retryBtn.addEventListener('click', () => {
    video.style.display = 'block';
    canvas.style.display = 'none';
    captureBtn.style.display = 'block';
    sendBtn.style.display = 'none';
    retryBtn.style.display = 'none';
});

sendBtn.addEventListener('click', () => {
    if (capturedImage) {
        tg.sendData(capturedImage);
    }
});
