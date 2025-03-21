

RPI = False
try:
    if RPI:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration())
    else:
        import cv2
        camera = cv2.VideoCapture(0)
except Exception as e:
    print(f"Error opening camera")
    raise ValueError(f"Error opening camera")

def get_camera_dimensions():
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return frame_width, frame_height

def generate_frames():
    if RPI:
        picam2.start()
    try:
        while True:

            if RPI:
                frame = picam2.capture_array()

            else:
                success, frame = camera.read()
                if not success:
                    break  # Stop if the camera fails
            # Yield the frame in multipart format
            yield encode_image(frame)

    except KeyboardInterrupt:
        if RPI:
            picam2.stop()
        
def encode_image(frame: cv2.typing.MatLike):
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()

    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')