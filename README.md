# 🌙 PRO Night Vision Hand Gesture Controller

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> Control Asphalt 8 Airborne using hand gestures — even in **complete darkness** or low-light conditions. No keyboard, no controller, just your hand!

---

## 🎮 Demo

📹 **Watch it in action:** [Click here to watch demo](https://youtu.be/4Ni2UHpvAhI)

---

## ✨ What Makes This Special?

This is an **upgraded version** of a standard gesture controller with a built-in **Pro Night Vision engine**. Most gesture controllers fail in dark rooms — this one doesn't.

The night vision pipeline uses:
- **Brightness & contrast boost** via `convertScaleAbs`
- **Gamma correction** to lift shadows without blowing out highlights
- **CLAHE (Contrast Limited Adaptive Histogram Equalization)** on the Y channel in YUV space for smart local contrast
- **Gaussian blur** for noise reduction in grainy low-light frames

All of this happens before MediaPipe processes the frame — so hand detection stays reliable even with poor lighting.

---

## 🕹️ Gesture Controls

| Gesture | Action | Key |
|---|---|---|
| ✋ Move hand **left** (x < 0.43) | Steer Left | ← Arrow |
| ✋ Move hand **right** (x > 0.57) | Steer Right | → Arrow |
| ☝️ **Index finger** up only | Nitro Boost | Space + ↑ |
| ✌️ **Index + Middle** fingers up | Brake | ↓ Arrow |
| 🤚 All fingers down | Accelerate | ↑ Arrow |
| 🚫 No hand detected | Auto Pause | Escape |
| 🤚 Hand reappears | Auto Resume | Escape |

> Steering uses **exponential smoothing** (factor 0.7) so movements feel natural, not jittery.

---

## 🧠 How It Works

```
Webcam captures frame (320x240 for low latency)
        ↓
Night Vision Enhancement Pipeline:
  → Brightness boost (alpha=1.8, beta=40)
  → Gamma correction (γ=1.5)
  → CLAHE on YUV Y-channel
  → Gaussian blur (5x5) for noise reduction
        ↓
MediaPipe HandLandmarker (VIDEO mode)
  → Detects 21 hand landmarks
  → Tracks single hand
        ↓
Gesture Logic:
  → Hand X position → Steer left/right
  → Finger state → Gas / Nitro / Brake
  → No hand → Pause game
        ↓
PyAutoGUI simulates keyboard inputs
        ↓
🚗 Asphalt 8 responds in real time!
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.8+ | Core language |
| OpenCV | Camera capture + night vision processing |
| MediaPipe Tasks (HandLandmarker) | 21-point hand landmark detection |
| PyAutoGUI | Keyboard simulation |
| NumPy | Gamma correction lookup table |
| keyboard | Quit key detection |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or above
- Webcam
- Asphalt 8 Airborne installed on PC (Windows)
- Download `hand_landmarker.task` model from [MediaPipe Models](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)

### Step 1 — Clone the repository
```bash
git clone https://github.com/vidhyasagar-alt/night-vision-gesture-controller.git
cd night-vision-gesture-controller
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set your model path
Open `pronightvisioncontrol.py` and update this line to where you saved the model:
```python
MODEL_PATH = r"D:\YOUR_PATH\hand_landmarker.task"
```

### Step 4 — Run the controller
```bash
python pronightvisioncontrol.py
```

### Step 5 — Play!
1. Open **Asphalt 8 Airborne** on your PC
2. Run the script — the webcam window will open
3. Place your hand in front of the camera
4. Start racing! 🏁
5. Remove your hand to auto-pause, show it again to resume

---

## 📦 Requirements

```
opencv-python
mediapipe
pyautogui
keyboard
numpy
```

---

## 📁 Project Structure

```
night-vision-gesture-controller/
│
├── pronightvisioncontrol.py   # Main script — run this
├── requirements.txt           # All required libraries
└── README.md                  # Project documentation
```

> **Note:** You need to download `hand_landmarker.task` separately from MediaPipe and set its path in the script.

---

## 🌙 Night Vision Pipeline (Technical Deep Dive)

```python
# Step 1 — Brightness & Contrast boost
frame = cv2.convertScaleAbs(frame, alpha=1.8, beta=40)

# Step 2 — Gamma correction (lifts dark areas)
gamma = 1.5
table = np.array([((i / 255.0) ** (1/gamma)) * 255 for i in range(256)]).astype("uint8")
frame = cv2.LUT(frame, table)

# Step 3 — CLAHE on YUV (smart local contrast)
img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
frame = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

# Step 4 — Gaussian blur (noise reduction)
frame = cv2.GaussianBlur(frame, (5,5), 0)
```

---

## 🎯 Key Features

- ✅ Works in **low-light and dark rooms**
- ✅ Real-time hand gesture detection
- ✅ Smooth steering with **exponential smoothing**
- ✅ Auto pause/resume when hand leaves frame
- ✅ 5 gesture controls — steer, nitro, brake, gas, pause
- ✅ 21-point landmark detection via MediaPipe
- ✅ Low resolution (320x240) for **ultra-low latency**
- ✅ No external hardware — just a webcam!

---

## 🔮 Future Improvements

- [ ] Two-hand gesture support
- [ ] Adjustable night vision sensitivity via GUI
- [ ] Support for other racing games
- [ ] Head gesture support for additional controls
- [ ] Mobile phone camera support via IP Webcam

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `HAND LOST` even in good light | Change `CAP_PROP_EXPOSURE` from `-5` to `-3` |
| Model not found error | Check that `MODEL_PATH` points to correct `.task` file |
| Game not responding | Make sure Asphalt 8 window is in focus |
| High latency | Lower resolution further: `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 240)` |

---

## 👨‍💻 About the Developer

<div align="center">

**Vidhya Sagar**

🎓 Final Year B.E. ECE Student (Graduating April 2026) &nbsp;|&nbsp; 🏫 Podhigai College of Engineering and Technology

💡 Passionate about AI, Computer Vision and Embedded Systems

[![GitHub](https://img.shields.io/badge/GitHub-vidhyasagar--alt-black?style=for-the-badge&logo=github)](https://github.com/vidhyasagar-alt)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/vidhya-sagar-4bba5339b)
[![Email](https://img.shields.io/badge/Email-Contact-red?style=for-the-badge&logo=gmail)](mailto:vidhyasagarboomi@gmail.com)

</div>

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify and share!

---

<div align="center">

⭐ **If this project helped you or impressed you, please give it a star!** ⭐

Made with ❤️ and a lot of late nights by **Vidhya Sagar** — ECE Department, Podhigai College of Engineering and Technology

</div>
