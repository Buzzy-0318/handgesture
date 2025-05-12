import cv2
import mediapipe as mp
import pyautogui
import time
import math
import threading

# Use laptop camera
cap = cv2.VideoCapture(0)

screen_w, screen_h = pyautogui.size()

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Gesture state variables
click_flag = False
double_pinch_time = 0
triple_pinch_time = 0
zoom_enabled = False
close_palm_count = 0
last_close_palm_time = 0
palm_close_triggered = False

# Frame sharing and control
latest_frame = None
exit_flag = False

def get_finger_states(landmarks):
    fingers = []
    tip_ids = [4, 8, 12, 16, 20]
    fingers.append(landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x)  # Thumb
    for i in range(1, 5):
        fingers.append(landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y)
    return fingers

def euclidean(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def gesture_recognition():
    global click_flag, double_pinch_time, triple_pinch_time, zoom_enabled
    global close_palm_count, last_close_palm_time, palm_close_triggered, latest_frame, exit_flag

    last_scroll_y = None

    while not exit_flag:
        success, img = cap.read()
        if not success:
            print("Camera error")
            break

        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark
            finger_states = get_finger_states(lm)

            # 👇 Draw landmarks directly on the image shown
            mp_draw.draw_landmarks(img, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

            # Cursor movement (index only)
            if finger_states[1] and not any(finger_states[2:]):
                x, y = int(lm[8].x * w), int(lm[8].y * h)
                pyautogui.moveTo(screen_w * x / w, screen_h * y / h)

            # Scroll with two fingers (index + middle)
            if finger_states[1] and finger_states[2] and not any(finger_states[3:]):
                scroll_y = lm[12].y
                if last_scroll_y is not None:
                    diff = scroll_y - last_scroll_y
                    if abs(diff) > 0.01:
                        pyautogui.scroll(-100 if diff > 0 else 100)
                last_scroll_y = scroll_y
            else:
                last_scroll_y = None

            # Pinch gesture (index + thumb)
            pinch_dist = euclidean(lm[4], lm[8])
            now = time.time()

            if pinch_dist < 0.03 and not click_flag:
                click_flag = True
                pyautogui.click()

                # Double pinch → double click
                if now - double_pinch_time < 0.5:
                    pyautogui.doubleClick()
                double_pinch_time = now
            elif pinch_dist >= 0.05:
                click_flag = False

            # Triple pinch toggle zoom
            if sum(finger_states[:4]) == 4 and pinch_dist < 0.03:
                if now - triple_pinch_time < 0.5:
                    zoom_enabled = not zoom_enabled
                    print("Zoom Enabled" if zoom_enabled else "Zoom Disabled")
                triple_pinch_time = now

            # Zoom with pinch if enabled
            if zoom_enabled:
                zoom_distance = euclidean(lm[4], lm[8])
                if zoom_distance > 0.2:
                    pyautogui.hotkey('ctrl', '+')
                elif zoom_distance < 0.1:
                    pyautogui.hotkey('ctrl', '-')

            # Double palm close → toggle desktop
            if sum(finger_states[1:5]) == 0:
                if now - last_close_palm_time < 0.8:
                    close_palm_count += 1
                else:
                    close_palm_count = 1
                last_close_palm_time = now

                if close_palm_count == 1 and not palm_close_triggered:
                    palm_close_triggered = True
                elif close_palm_count == 1 and palm_close_triggered:
                    pyautogui.hotkey('win', 'd')
                    palm_close_triggered = False
                    close_palm_count = 0

        # Show hand model and update latest frame
        latest_frame = img.copy()

# Run gesture recognition in background thread
gesture_thread = threading.Thread(target=gesture_recognition)
gesture_thread.daemon = True
gesture_thread.start()

# Show live camera window
while True:
    if latest_frame is not None:
        cv2.imshow("Live Gesture Cam", latest_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit_flag = True
        break

cap.release()
cv2.destroyAllWindows()
