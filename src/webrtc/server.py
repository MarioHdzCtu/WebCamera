import json
import traceback
import cv2
from fastapi import FastAPI, WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaBlackhole
from av import VideoFrame

app = FastAPI()
pcs = set()  # Keep track of active WebRTC connections

class CameraStreamTrack(MediaStreamTrack):
    """WebRTC Video Track from Raspberry Pi Camera"""
    kind = "video"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            raise RuntimeError("❌ Failed to open camera!")

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()
        if not ret:
            print("❌ Failed to capture frame")
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        print("Frame received successfully")
        return video_frame

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebRTC signaling between the client and the Raspberry Pi"""
    await websocket.accept()
    
    pc = RTCPeerConnection()
    pcs.add(pc)  # Track active connections

    # Add the camera stream to the peer connection
    camera = CameraStreamTrack()
    pc.addTrack(camera)

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data["type"] == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                
                # Create and send an answer
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                
                await websocket.send_text(json.dumps({
                    "type": "answer",
                    "sdp": pc.localDescription.sdp
                }))

    except Exception as e:
        print(f"WebSocket error: {e}")
        traceback.print_exc()
    finally:
        pcs.remove(pc)
        await pc.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
