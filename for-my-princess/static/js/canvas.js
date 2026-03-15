// ── Canvas Setup ──
const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');

let painting = false;
let currentColor = '#000000';
let currentTool = 'pencil';
let brushSize = 4;
let history = [];

// Save initial blank state
saveState();

// ── Tool & Colour Pickers ──
document.querySelectorAll('.color-swatch').forEach(swatch => {
    swatch.addEventListener('click', () => {
        document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
        swatch.classList.add('active');
        currentColor = swatch.dataset.color;
    });
});

document.getElementById('customColor').addEventListener('input', e => {
    currentColor = e.target.value;
    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
});

document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tool-btn[data-tool]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentTool = btn.dataset.tool;
    });
});

document.getElementById('brushSize').addEventListener('input', e => {
    brushSize = parseInt(e.target.value);
});

// ── Undo / Clear ──
document.getElementById('undoBtn').addEventListener('click', () => {
    if (history.length > 1) {
        history.pop();
        const img = new Image();
        img.src = history[history.length - 1];
        img.onload = () => ctx.drawImage(img, 0, 0);
    }
});

document.getElementById('clearBtn').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    saveState();
});

// ── Drawing ──
canvas.addEventListener('mousedown', e => {
    painting = true;
    saveState();
    draw(e);
});

canvas.addEventListener('mousemove', e => {
    if (painting) draw(e);
});

canvas.addEventListener('mouseup', () => { painting = false; ctx.beginPath(); });
canvas.addEventListener('mouseleave', () => { painting = false; ctx.beginPath(); });

function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
}

function draw(e) {
    const pos = getPos(e);

    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    if (currentTool === 'eraser') {
        ctx.globalCompositeOperation = 'destination-out';
        ctx.strokeStyle = 'rgba(0,0,0,1)';
        ctx.lineWidth = brushSize * 3;
        ctx.globalAlpha = 1;
    } else if (currentTool === 'pencil') {
        ctx.globalCompositeOperation = 'source-over';
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = brushSize;
        ctx.globalAlpha = 0.9;
    } else if (currentTool === 'marker') {
        ctx.globalCompositeOperation = 'source-over';
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = brushSize * 2.5;
        ctx.globalAlpha = 0.6;
    } else if (currentTool === 'watercolor') {
        ctx.globalCompositeOperation = 'source-over';
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = brushSize * 4;
        ctx.globalAlpha = 0.15;
    }

    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

function saveState() {
    history.push(canvas.toDataURL());
    if (history.length > 30) history.shift();
}

// ── Touch Support ──
canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    painting = true;
    saveState();
    draw(toMouseEvent(e));
}, { passive: false });

canvas.addEventListener('touchmove', e => {
    e.preventDefault();
    if (painting) draw(toMouseEvent(e));
}, { passive: false });

canvas.addEventListener('touchend', () => { painting = false; ctx.beginPath(); });

function toMouseEvent(e) {
    const touch = e.touches[0];
    return { clientX: touch.clientX, clientY: touch.clientY };
}
