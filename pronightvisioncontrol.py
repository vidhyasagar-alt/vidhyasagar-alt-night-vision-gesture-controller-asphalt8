import cv2
import mediapipe as mp
import pyautogui
import time
import keyboard
import numpy as np

# ========== SETTINGS ==========
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# UPDATE THIS PATH to where YOUR hand_landmarker.task file is saved
MODEL_PATH = r"D:\PY project\hand_landmarker.task"

# ========== MEDIAPIPE SETUP ==========
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.3,   #  FIX: lowered for better low-light detection
    min_hand_presence_confidence=0.3,
    min_tracking_confidence=0.3
)

try:
    landmarker = HandLandmarker.create_from_options(options)
    print(" MediaPipe HandLandmarker loaded successfully!")
except Exception as e:
    print(f" Error loading model: {e}")
    print(" Make sure hand_landmarker.task exists at:", MODEL_PATH)
    exit()

# ========== CAMERA SETUP ==========
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print(" Camera not found! Check if webcam is connected.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 30)

#  FIX: Correct camera settings for low light
# DO NOT set AUTO_EXPOSURE to 1  that disables it on most webcams
# Let the camera auto-manage exposure for better brightness
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)   # 0.75 = auto mode ON for most webcams
cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)        # boost brightness
cap.set(cv2.CAP_PROP_CONTRAST, 50)           # slight contrast boost
cap.set(cv2.CAP_PROP_SATURATION, 60)

print(" Camera opened successfully!")

# ========== KEY STATES ==========
keys = {"up": False, "down": False, "left": False, "right": False}

def control(key):
    if key and not keys[key]:
        pyautogui.keyDown(key)
        keys[key] = True

def release(key):
    if keys[key]:
        pyautogui.keyUp(key)
        keys[key] = False

def release_all():
    for k in keys:
        if keys[k]:
            pyautogui.keyUp(k)
            keys[k] = False

# ========== NIGHT VISION ENHANCEMENT ==========
def enhance_for_night(frame):
    # Step 1: Brightness + contrast boost
    frame = cv2.convertScaleAbs(frame, alpha=1.8, beta=50)

    # Step 2: Gamma correction  lifts dark shadows
    gamma = 1.8
    inv_gamma = 1.0 / gamma
    table = np.array([
        ((i / 255.0) ** inv_gamma) * 255
        for i in np.arange(0, 256)
    ]).astype("uint8")
    frame = cv2.LUT(frame, table)

    # Step 3: CLAHE on YUV Y-channel  smart local contrast
    img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
    frame = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    # Step 4: Gentle noise reduction
    frame = cv2.GaussianBlur(frame, (3, 3), 0)

    return frame

# ========== PAUSE SYSTEM ==========
game_paused = False
hand_lost_frames = 0
HAND_LOST_THRESHOLD = 15  #  FIX: wait 15 frames before pausing (avoids false pauses)

def pause_game():
    global game_paused
    if not game_paused:
        release_all()
        pyautogui.press("escape")
        game_paused = True
        print("  Game PAUSED - hand lost")

def resume_game():
    global game_paused
    if game_paused:
        pyautogui.press("escape")
        game_paused = False
        print("  Game RESUMED - hand detected")

# ========== SMOOTHING ==========
prev_x = 0.5
smooth_factor = 0.6  #  FIX: slightly less smooth for faster response

# ========== MAIN LOOP ==========
print("PRO Night Vision Controller Active!")
print("Controls: Steer (move hand L/R) | Nitro (index up) | Brake (2 fingers up) | Gas (fist)")
print("Press Q to quit\n")

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(" Failed to read from camera. Retrying...")
        time.sleep(0.1)
        continue

    #  FIX: Flip FIRST, then enhance
    frame = cv2.flip(frame, 1)

    #  FIX: Enhance the frame ONCE, use same enhanced frame for BOTH MediaPipe AND display
    enhanced = enhance_for_night(frame)

    h, w, _ = enhanced.shape

    #  FIX: Send enhanced frame to MediaPipe (not raw frame)
    rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    ts = int(time.time() * 1000)
    result = landmarker.detect_for_video(mp_image, ts)

    status = "SEARCHING..."
    display = enhanced.copy()

    if result and result.hand_landmarks:
        hand_lost_frames = 0
        resume_game()

        landmarks = result.hand_landmarks[0]

        # ===== SMOOTH STEERING =====
        current_x = landmarks[5].x
        hand_x = smooth_factor * prev_x + (1 - smooth_factor) * current_x
        prev_x = hand_x

        # ===== STEER LEFT / RIGHT =====
        if hand_x < 0.40:
            control("left")
            release("right")
            status = "LEFT"
        elif hand_x > 0.60:
            control("right")
            release("left")
            status = "RIGHT"
        else:
            release("left")
            release("right")
            status = "STRAIGHT"

        # ===== FINGER DETECTION =====
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]

        index_up = index_tip.y < index_pip.y - 0.02   #  FIX: small threshold to avoid jitter
        middle_up = middle_tip.y < middle_pip.y - 0.02

        # ===== GAS / NITRO / BRAKE =====
        if index_up and not middle_up:
            pyautogui.press("space")
            control("up")
            release("down")
            status += " + NITRO"
        elif index_up and middle_up:
            control("down")
            release("up")
            status += " + BRAKE"
        else:
            control("up")
            release("down")
            status += " + GAS"

    else:
        #  FIX: Wait threshold frames before pausing to avoid false triggers
        hand_lost_frames += 1
        if hand_lost_frames >= HAND_LOST_THRESHOLD:
            pause_game()
            release_all()
        status = f"HAND LOST ({hand_lost_frames})"

    # ===== DRAW STEERING ZONE LINES =====
    cv2.line(display, (int(w * 0.40), 0), (int(w * 0.40), h), (0, 255, 255), 1)
    cv2.line(display, (int(w * 0.60), 0), (int(w * 0.60), h), (0, 255, 255), 1)

    # ===== DRAW STATUS =====
    cv2.rectangle(display, (0, 0), (w, 30), (0, 0, 0), -1)
    cv2.putText(display, status, (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # ===== DRAW PAUSE INDICATOR =====
    if game_paused:
        cv2.putText(display, "PAUSED", (w // 2 - 30, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("PRO Night Vision Controller", display)

    # ===== QUIT =====
    if cv2.waitKey(1) & 0xFF == ord('q') or keyboard.is_pressed('q'):
        print("\n Quitting...")
        break

    frame_count += 1

# ========== CLEANUP ==========
release_all()
cap.release()
cv2.destroyAllWindows()
landmarker.close()
print(" Closed cleanly.")