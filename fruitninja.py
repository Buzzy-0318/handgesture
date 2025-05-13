import cv2
import mediapipe as mp
import random
import time
import math

# Setup camera
cap = cv2.VideoCapture(0)
screen_w, screen_h = 1280, 720
cap.set(3, screen_w)
cap.set(4, screen_h)

# Setup mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Fruit properties
fruits = []
fruit_radius = 30
spawn_delay = 1.0
last_spawn_time = time.time()

# Score
score = 0

def euclidean(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# Main loop
while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    cursor = None

    # Draw hand and get fingertip
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        h, w, _ = frame.shape
        index_finger_tip = hand_landmarks.landmark[8]  # Index fingertip
        cursor = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
        cv2.circle(frame, cursor, 10, (0, 255, 0), -1)

    # Spawn fruit
    if time.time() - last_spawn_time > spawn_delay:
        x = random.randint(fruit_radius, screen_w - fruit_radius)
        fruits.append({'x': x, 'y': 0})
        last_spawn_time = time.time()

    # Update fruits
    for fruit in fruits[:]:
        fruit['y'] += 7  # falling speed
        center = (fruit['x'], fruit['y'])
        cv2.circle(frame, center, fruit_radius, (0, 0, 255), -1)

        # Collision check
        if cursor and euclidean(cursor, center) < fruit_radius:
            fruits.remove(fruit)
            score += 1

        # Remove if off screen
        elif fruit['y'] > screen_h:
            fruits.remove(fruit)

    # Show score
    cv2.putText(frame, f"Score: {score}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    cv2.imshow("Fruit Ninja - Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
