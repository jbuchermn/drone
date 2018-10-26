from .camera import StreamingMode, CameraConfig  # noqa F401

try:
    from .raspicam import RaspiCam
except Exception:
    print("RaspiCam not available")
    RaspiCam = None

try:
    from .v4l2cam import V4L2Cam
except Exception as err:
    print("V4L2Cam not available")
    print(err)
    V4L2Cam = None

if RaspiCam is None and V4L2Cam is None:
    raise Exception("Could not find camera backend")

Camera = RaspiCam if RaspiCam is not None else V4L2Cam
