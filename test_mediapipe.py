import mediapipe as mp
print(mp.__version__)
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

model_path = "face_landmarker.task"
print(f"Model exists: {os.path.exists(model_path)}")

try:
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrix=False,
        num_faces=1)
    landmarker = vision.FaceLandmarker.create_from_options(options)
    print("SUCCESS: Landmarker initialized.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
