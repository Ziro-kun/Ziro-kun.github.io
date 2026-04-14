import sys
try:
    import cv2
except ImportError:
    print("cv2 not installed")
    sys.exit(0)

image_path = 'src/assets/about-hero.png'
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface.xml')
faces = face_cascade.detectMultiScale(gray, 1.1, 3)

if len(faces) > 0:
    x, y, w, h = faces[0]
    print(f"Cat face found at: x={x}, y={y}, w={w}, h={h}")
    # Approximate eyes inside the face
    # Usually eyes are in the upper half, around 1/3 and 2/3 of the width
    left_eye_x = x + w * 0.3
    right_eye_x = x + w * 0.7
    eye_y = y + h * 0.4
    print(f"Est. Left Eye (viewer left) : {int(left_eye_x)}, {int(eye_y)}")
    print(f"Est. Right Eye (viewer right): {int(right_eye_x)}, {int(eye_y)}")
else:
    print("Cat face not found")
