from .camera import StreamingMode, CameraConfig  # noqa F401

try:
    from .raspicam import RaspiCam
    print("Found raspicam backend")
except Exception:
    RaspiCam = None

try:
    from .v4l2cam import V4L2Cam
    print("Found V4L2 backend")
except Exception as err:
    V4L2Cam = None

if RaspiCam is None and V4L2Cam is None:
    raise Exception("Could not find camera backend")

Camera = RaspiCam if RaspiCam is not None else V4L2Cam
