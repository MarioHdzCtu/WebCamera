import cv2

cap = cv2.VideoCapture(0)  # Open the default camera
if not cap.isOpened():
    print("❌ Camera not detected. Check camera connection.")
else:
    print("✅ Camera detected successfully.")

ret, frame = cap.read()
if ret:
    print("✅ Camera is capturing frames.")
    cv2.imwrite("test.jpg", frame)  # Save a test image
else:
    print("❌ Failed to capture frame.")

cap.release()
