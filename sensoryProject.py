import os
import sys
import errno
import numpy as np
import sounddevice as sd
import cv2


if sys.version[:1] != "3":
    raise Exception("Python version is not 3.X (atleast 3.0)")

vid_FILE = None
sound_File = None


# Retrive user video
filename = input("\nPlease enter the name of the video file (i.e. timvid.mp4):\n")
if os.path.exists(filename):
    vid_FILE = os.path.abspath(filename)
    print("\n\t'%s' file found!" % filename)
else:
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)


# Check for file 'sensoryProject.txt' existance
if os.path.exists("sensoryProject.txt"):
    sound_FILE = os.path.relpath("sensoryProject.txt")
    f = open(sound_FILE, "r+")
    f.truncate(0)
else:
    f = open("sensoryProject.txt", "x")
    sound_FILE = os.path.relpath("sensoryProject.txt")

f.close()
print("\n\t'sensoryProject.txt' CLEARED/INITIALIZED")



# FUNCTION: frames captures a video
#   Input:  Video file director
#   Output: A GENERATOR object for the frames of a video
def get_next_frame(filepath):
    video = cv2.VideoCapture(filepath)
    while video.isOpened():
        rete,frame = video.read()
        if rete:    yield frame
        else:       break
    video.release()
    yield None


# FUNCTION: retrieves volume data from 'sensoryProject.txt'
#   output: float value for volume
def get_volume():
    volume = 1
    f = open(sound_FILE, "r")
    try:
        volume = f.readlines()[0]
        volume = volume.strip()
    except:
        print("ERROR: VOLUME READ FAILURE")
    f.close()

    volume = float(volume)
    if volume < 1:  volume = 1      # Volume input minimum of 1
    return volume



# FUNCTION: loops through the frames of a video and applies the saturation aspect depending on volume
#   Input:  Video file director
def vidLoop(filepath):
    stream.start()      # Start audio stream (stream) on the first loop
    frames = get_next_frame(filepath)
    frame = frames.__next__()

    while(frames != None):
        # Increases the saturation of frame by mic input value (volume) 
        volume = get_volume()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1] * volume
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        frame = cv2.resize(frame, (1280, 720))          # Resize frame
        cv2.imshow('sensoryProject', frame)             # Display frame
        frame = frames.__next__()                       # Grab next frame

        # if 'Esc' is hit, stop Audio Stream and exit program
        if cv2.waitKey(10) == 27:
            print("\nEXITING...")
            stream.stop()
            return

    # RESTART the video if the end is reached
    print("\nRESTART...\n")
    vidLoop(filename)


# FUNCTION:  processes the volumn input data
#   Input: the mic input data for volumn
def frame_callback(indata, frames, time, status):
    sensitivity = 10    # 10 is default

    # Takes the incoming data and converts it to volume data
    volume_norm = np.linalg.norm(indata) * sensitivity

    f = open(sound_FILE, "r+")      
    f.write(str(volume_norm))                   # Stores volume data in 'sensoryProject.txt'
    f.close()
    print("|" * int(volume_norm))               # Volume terminal visual



if __name__ == "__main__":
    print("\tINITIALZING AUDIO STREAM...")
    stream = sd.InputStream(        # Initializing audio stream
        samplerate = 44100,         # Standard Sample Rate
        blocksize = 512,            # Returns input at 512th frame
        channels = 1,
        device = sd.default.device,     # Default input device
        callback = frame_callback)      # Volumn processing FUNCTION
    print("\tAUDIO STREAM INITIALIZED!\n\n")

    cv2.namedWindow('sensoryProject', cv2.WINDOW_NORMAL)

    print("\tPLAYING VIDEO...\n")
    print("\tTo exit the program, press 'ESC' on the second window")
    vidLoop(filename)
    
    cv2.destroyAllWindows()
