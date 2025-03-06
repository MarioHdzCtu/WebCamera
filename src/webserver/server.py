from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from src.camera.capture import generate_frames, get_camera_dimensions
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

some_file_path = "otro_video.mp4"
app = FastAPI()
app.mount("./src/webserver/templates", StaticFiles(directory="/src/webserver/templates"), name="templates")
templates = Jinja2Templates(directory="templates")

@app.get("/video-example")
def main():
    def iterfile(): 
        with open(some_file_path, mode="rb") as file_like: 
            yield from file_like 

    return StreamingResponse(iterfile(), media_type="video/mp4")


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    w, h = get_camera_dimensions()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"w": w, "h": h}
    )