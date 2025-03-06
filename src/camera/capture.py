import cv2

camera = cv2.VideoCapture(0)

def get_camera_dimensions():
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return frame_width, frame_height

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break  # Stop if the camera fails
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)

        # Convert to bytes
        frame_bytes = buffer.tobytes()

        # Yield the frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')