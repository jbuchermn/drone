from .camera import StreamingMode, CameraConfig

try:
    from .raspicam import RaspiCam
except Exception:
    RaspiCam = None

try:
    from .v4l2cam import V4L2Cam
except Exception:
    V4L2Cam = None

if RaspiCam is None and V4L2Cam is None:
    raise Exception("Could not find camera backend")

Camera = RaspiCam if RaspiCam is not None else V4L2Cam
