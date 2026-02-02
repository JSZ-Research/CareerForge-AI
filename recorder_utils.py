import av
import cv2
import os
import time
import threading
import mediapipe as mp
# ... imports

class FaceMeshProcessor(VideoTransformerBase):
    def __init__(self):
        # ...
        self.start_time = 0
        self.lock = threading.Lock()
        # ...

    def start_recording(self):
        with self.lock:
            self.record = True
            self.start_time = time.time() # Start Clock
            self.container = av.open(self.output_file, mode="w")
            self.stream = self.container.add_stream("h264", rate=30)
            self.stream.pix_fmt = "yuv420p"
            self.stream.options = {'crf': '23'}

    def stop_recording(self):
        with self.lock:
            self.record = False
            if self.container:
                for packet in self.stream.encode():
                    self.container.mux(packet)
                self.container.close()
                self.container = None
                return self.output_file
        return None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # MediaPipe Processing
        used_mediapipe = False
        if self.landmarker:
            try:
                # Convert to MP Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                detection_result = self.landmarker.detect(mp_image)
                
                if detection_result.face_landmarks:
                    for face_landmarks in detection_result.face_landmarks:
                        # Draw Mesh Points
                        for landmark in face_landmarks:
                            h, w, _ = img.shape
                            lx, ly = int(landmark.x * w), int(landmark.y * h)
                            cv2.circle(img, (lx, ly), 1, (0, 255, 128), -1) # Sci-fi Green Dot
                    used_mediapipe = True
            except Exception as e:
                print(f"MP Infer Error: {e}")
        
        # Fallback visualization if MP failed or found no face
        if not used_mediapipe:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(img, "OpenCV Fallback", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Overlay
        status_color = (0, 0, 255) if self.record else (0, 255, 0)
        status_text = "REC" if self.record else "AI VISION: " + ("Go" if used_mediapipe else "Basic")
        cv2.putText(img, status_text, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        if self.record:
            cv2.circle(img, (15, 25), 8, (0, 0, 255), -1)

        # Record
        with self.lock:
            if self.record and self.container:
                # Timer Logic
                elapsed = time.time() - self.start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                timer_text = f"{minutes:02}:{seconds:02}"
                
                # Color logic
                if elapsed < 90:
                    timer_color = (0, 255, 0) # Green
                elif elapsed < 120:
                    timer_color = (0, 255, 255) # Yellow
                else:
                    timer_color = (0, 0, 255) # Red
                    timer_text += " (WRAP UP!)"

                # Draw Timer (Bottom Right)
                h, w, _ = img.shape
                cv2.putText(img, timer_text, (w - 250, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, timer_color, 2)

                new_av_frame = av.VideoFrame.from_ndarray(img, format="bgr24")
                for packet in self.stream.encode(new_av_frame):
                    self.container.mux(packet)
                    
        return av.VideoFrame.from_ndarray(img, format="bgr24")
