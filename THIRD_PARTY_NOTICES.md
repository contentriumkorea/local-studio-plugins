# Third-party components

This package contains independently authored Pin Local / Glam Local code and the following components. Their original notices and licenses are retained in the packaged runtime, principally `runtime/LICENSE.txt` and `runtime/Lib/site-packages/*dist-info/`. No code or artwork from the commercial reference plugins is included.

- CPython 3.13.16, Python Software Foundation license. https://www.python.org/
- Python standalone distribution from python-build-standalone. Its bundled licenses are retained with the runtime. https://github.com/astral-sh/python-build-standalone
- OpenCV contrib Python 4.13.0.92, Apache 2.0; bundled FFmpeg and other third parties have separate terms in `opencv_contrib_python-4.13.0.92.dist-info/LICENSE-3RD-PARTY.txt`. https://github.com/opencv/opencv-python
- MediaPipe 0.10.35, Apache 2.0. https://github.com/google-ai-edge/mediapipe
- MediaPipe Face Landmarker float16 task model, distributed by Google: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task
- NumPy 2.5.4, BSD-3-Clause and bundled numerical library notices. https://numpy.org/
- MediaPipe dependencies include absl-py, CFFI, flatbuffers, Matplotlib, Pillow, sounddevice, and their dependencies. Their installed metadata and license files are retained. See `runtime-packages.txt` for versions.
- json2.js by Douglas Crockford, Public Domain. Copyright/license header retained in the signed CEP package. https://github.com/douglascrockford/JSON-js

The native effect is built using Adobe's After Effects SDK. The SDK, its sample tools, and ZXPSignCmd are development dependencies and are not distributed in this package. Adobe, Premiere Pro and After Effects are trademarks of Adobe. This project is not an Adobe product or an affiliate of the commercial reference plugins.
