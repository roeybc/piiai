import cv2
from face_recognizer import FaceRecognizer

# Open the video file
def redact_video(video_path, video_output):
    face_ercognizer = FaceRecognizer()

    # Open the input video
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    # Create a VideoWriter object
    out = cv2.VideoWriter(video_output, codec, fps, (width, height))

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if not success:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_ercognizer.recognize(rgb_frame)

        for result in results:
            frame = cv2.rectangle(frame, result.bounding_box, (0,0,0), cv2.FILLED)
            frame = cv2.putText(frame, f'Confidence: {result.confidence_score:.2f}', (result.bounding_box[0], result.bounding_box[1]-20), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 2)

        out.write(frame)

    # Release the video capture object and close the display window
    cap.release()
    out.release()