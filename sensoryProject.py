import os
import sys
import numpy as np
import sounddevice as sd
import cv2


vid_FILE = None
stream = None
CHUNK = 2048


# FUNCTION: Finds user video
#   Output: relative path to video file
def find_Video():
    while True:
        filename = input("Please enter the name of the video file (i.e. timvid.mp4):\n")
        if os.path.exists(filename):
            print("\n\t'%s' file found!" % filename)
            return os.path.relpath(filename)
        else:
            print("\n\tFILE NOT FOUND. Please Try Again\n")


# FUNCTION: Initiates sounddevice stream 
#   Output: sounddevice input stream
def init_stream():
    print("\n\tAUDIO STREAM INITIALIZED!\n") 
    return sd.InputStream(
        samplerate = 44100,           # Standard Sample Rate
        blocksize = CHUNK,            # Returns input at 512th frame
        channels = 1,
        device = sd.default.device,   # Default input device
    )  


# FUNCTION: frames captures a video
#   Input:  Video file director
#   Output: A GENERATOR object for the frames of a video
def get_frames():
    video = cv2.VideoCapture(vid_FILE)
    while video.isOpened():
        rete,frame = video.read()
        if rete:    yield frame
        else:       break
    video.release()
    yield None


# FUNCTION: Takes incoming stream data and converts it to float values
#   Output: a float that represents the volume of the mic input
def process_volume(prev_volume):
    volume = prev_volume
    sensitivity = 10    # 10 is default

    # Takes the incoming data and converts it to volume data
    if (stream.read_available >= CHUNK):
        indata, overflow = stream.read(CHUNK)
        volume = np.linalg.norm(indata) * sensitivity
        if volume < 1:  volume = 1      # Volume minimum of 1
    print("|" * int(volume))            # Volume terminal visual
    return volume



# FUNCTION: loops through the frames of a video and applies the saturation aspect depending on volume
def vidLoop():
    stream.start()
    frames = get_frames()
    volume = 1

    while True:
        frame = frames.__next__()
        try:    frame.all()
        except:
            frames = get_frames()
            frame = frames.__next__()
            print("\nRESTART...\n")

        volume = process_volume(volume)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1] * volume
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        frame = cv2.resize(frame, (1280, 720))          # Resize frame
        cv2.imshow('sensoryProject', frame)             # Display frame

        if cv2.waitKey(10) == 27:
            print("\nEXITING...")
            stream.stop()
            return



if __name__ == "__main__":
    if sys.version[:1] != "3":
        raise Exception("Python version is not 3.X (atleast 3.0)")

    vid_FILE = find_Video()
    stream = init_stream()

    cv2.namedWindow('sensoryProject', cv2.WINDOW_NORMAL)
    print("\tPLAYING VIDEO...")
    print("\tTo exit the program, press 'ESC' on the second window\n")
    vidLoop()
    
    cv2.destroyAllWindows()