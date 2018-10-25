from .python_space_camera import PythonSpaceCamera

raise Exception("Not yet implemented")


class V4L2Cam(PythonSpaceCamera):
    def __init__(self, gallery, ws_port):
        super().__init__(gallery, ws_port)
