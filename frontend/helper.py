import threading
from threading import Lock

import requests
from ultralytics import YOLO
import streamlit as st
import cv2
import yt_dlp
import settings


class Camera:
    last_frame = None
    last_ready = None
    lock = Lock()

    def __init__(self, rtsp_link: str):
        capture = cv2.VideoCapture(rtsp_link)
        thread = threading.Thread(target=self.rtsp_cam_buffer, args=(
            capture,), name="rtsp_read_thread")
        thread.daemon = True
        thread.start()

    def rtsp_cam_buffer(self, capture):
        while True:
            with self.lock:
                self.last_ready, self.last_frame = capture.read()

    def getFrame(self):
        if (self.last_ready is not None) and (self.last_frame is not None):
            return self.last_frame.copy()
        else:
            return None


def load_model(model_path):
    """
    Loads a YOLO object detection model from the specified model_path.

    Parameters:
        model_path (str): The path to the YOLO model file.

    Returns:
        A YOLO object detection model.
    """
    model = YOLO(model_path)
    return model


def display_tracker_options():
    # columns = st.columns(2)

    # with columns[0]:
    #     display_tracker = st.radio("Display Tracker", ('Yes', 'No'))
    #     is_display_tracker = True if display_tracker == 'Yes' else False
    # with columns[1]:
    #     if is_display_tracker:
    #         tracker_type = st.radio("Tracker", ("bytetrack.yaml", "botsort.yaml"))
    #         return is_display_tracker, tracker_type
    # return is_display_tracker, None

    return "Yes", "bytetrack.yaml"


def _display_detected_frames(conf, model, st_frame, image, is_display_tracking=None, tracker=None):
    """
    Display the detected objects on a video frame using the YOLOv8 model.

    Args:
    - conf (float): Confidence threshold for object detection.
    - model (YoloV8): A YOLOv8 object detection model.
    - st_frame (Streamlit object): A Streamlit object to display the detected video.
    - image (numpy array): A numpy array representing the video frame.
    - is_display_tracking (bool): A flag indicating whether to display object \
        tracking (default=None).

    Returns:
    None
    """

    # Resize the image to a standard size
    try:
        image = cv2.resize(image, (720, int(720*(9/16))))
    except Exception as e:
        print("Can't resize the frame. Returning to default size. \
            Reason:", str(e))
        image = image

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True, tracker=tracker)
    else:
        # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf)

    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    st_frame.image(res_plotted,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )


def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'no_warnings': True,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']


def play_youtube_video(conf, model):
    source_youtube = st.sidebar.text_input("YouTube Video url")
    is_display_tracker, tracker = display_tracker_options()

    if st.sidebar.button('Detect Objects'):
        if not source_youtube:
            st.sidebar.error("Please enter a YouTube URL")
            return

        try:
            st.sidebar.info("Extracting video stream URL...")
            stream_url = get_youtube_stream_url(source_youtube)

            st.sidebar.info("Opening video stream...")
            vid_cap = cv2.VideoCapture(stream_url)

            if not vid_cap.isOpened():
                st.sidebar.error(
                    "Failed to open video stream. Please try a different video.")
                return

            st.sidebar.success("Video stream opened successfully!")
            st_frame = st.empty()
            while vid_cap.isOpened():
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(
                        conf,
                        model,
                        st_frame,
                        image,
                        is_display_tracker,
                        tracker
                    )
                else:
                    break

            vid_cap.release()

        except Exception as e:
            st.sidebar.error(f"An error occurred: {str(e)}")


def play_rtsp_stream(conf, model):
    """
    Plays an rtsp stream. Detects Objects in real-time using the YOLOv8 object\
        detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    st.sidebar.header("Add New Stream")

    new_rtsp_url = st.sidebar.text_input("Enter RTSP URL")
    st.sidebar.caption(
        'Example URL: rtsp://admin:12345@192.168.1.210:554/Channels/101')
    if st.sidebar.button("Add Stream"):
        if new_rtsp_url:
            response = requests.post(
                f"{settings.backend_url}/streams/", json={"url": new_rtsp_url})
            if response.status_code == 200:
                st.sidebar.success("Stream added successfully!")
            elif response.status_code == 409:
                st.sidebar.warning("Stream already registered.")
            else:
                st.sidebar.error(f"Error: {response.json()['detail']}")
        else:
            st.sidebar.error("Please enter a valid RTSP URL.")

    # Fetch and display the list of registered RTSP streams
    streams_response = requests.get(f"{settings.backend_url}/streams/")
    if streams_response.status_code == 200:
        streams = streams_response.json()
        stream_options = {stream['url']: stream['id'] for stream in streams}

        # Section to select and remove streams
        st.sidebar.header("Select Stream to View")
        selected_rtsp_url = st.sidebar.selectbox(
            "Select a stream", list(stream_options.keys()))

        # Section to remove a stream
        if st.sidebar.button("Remove Stream"):
            rtsp_id = stream_options[selected_rtsp_url]
            response = requests.delete(
                f"{settings.backend_url}/streams/{rtsp_id}")
            if response.status_code == 200:
                st.sidebar.success("Stream removed successfully!")
            else:
                st.sidebar.error(f"Error: {response.json()['detail']}")

        is_display_tracker, tracker = display_tracker_options()
        if st.sidebar.button('Start Streaming'):

            capture = Camera(selected_rtsp_url)

            st_frame = st.empty()

            while True:
                image = capture.getFrame()
                _display_detected_frames(conf,
                                         model,
                                         st_frame,
                                         image,
                                         is_display_tracker,
                                         tracker
                                         )
    else:
        st.sidebar.error(
            f"Failed to load streams: ({streams_response.status_code})")


def play_webcam(conf, model):
    """
    Plays a webcam stream. Detects Objects in real-time using the YOLOv8 \
        object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    source_webcam = settings.WEBCAM_PATH
    is_display_tracker, tracker = display_tracker_options()
    if st.sidebar.button('Detect Objects'):
        try:
            vid_cap = cv2.VideoCapture(source_webcam)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker,
                                             )
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))


def play_stored_video(conf, model):
    """
    Plays a stored video file. Tracks and detects objects in real-time using \
        the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    source_vid = st.sidebar.selectbox(
        "Choose a video...", settings.VIDEOS_DICT.keys())

    is_display_tracker, tracker = display_tracker_options()

    # with open(settings.VIDEOS_DICT.get(source_vid), 'rb') as video_file:
    #     video_bytes = video_file.read()
    # if video_bytes:
    #     st.video(video_bytes)

    if st.sidebar.button('Detect Video Objects'):
        try:
            vid_cap = cv2.VideoCapture(
                str(settings.VIDEOS_DICT.get(source_vid)))
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))
