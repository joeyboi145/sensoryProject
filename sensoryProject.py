# Version 5.0 (latest): deepfry_v5.0.py
#   by Joe Martinez   (12/20/2022)
#
# Description:
#   An algorithm that increases the saturation of a video
#   depending on the mic input volume. Algorithm resign from
#   previous version
#
# Requirements:
#   Python Version 3.X (atleast 3.0)
#   A video file

import os
import sys
import errno

import numpy as np
import sounddevice as sd
import cv2


# Chech user's Python version 3.X
if sys.version[:1] != "3":
    raise Exception("Python version is not 3.X (atleast 3.0)")

# Ask user for VIDEO filename
filename = input("\nPlease enter the name of the video file (i.e. timvid.mp4):\n")

# Check for VIDEO file's existance
if os.path.exists(filename):
    vid_FILE = os.path.abspath(filename)    # If so, store file's directory
    print("\n\t'%s' file found!" % filename)
else:                                       # If not, raise error
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)


# Check for file 'deepfry_volume.txt' existance
if os.path.exists("deepfry_volume.txt"):
    sound_FILE = os.path.abspath("deepfry_volume.txt")  # If so, store 'deepfry_volume.txt' directory
    f = open(sound_FILE, "r+")                          #   &    clears previous data 
    f.truncate(0)
else:
    f = open("deepfry_volume.txt", "x")                 # If not, creates new text file
    sound_FILE = os.path.abspath("deepfry_volume.txt")  #   &     store file's directory

f.close()
test_volumn = None
print("\n\t'deepfry_volume.txt' CLEARED/INITIALIZED")



# FUNCTION that frames captures a video
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


# FUNCTION that loops through the frames of a video and applies the deepfry aspect depending on volume
#   Input:  Video file director
def vidLoop(filepath):
    volume = 1          # Mic input volume
    stream.start()      # Start audio stream (stream) on the first loop
    frames = get_next_frame(filepath)
    frame = frames.__next__()

    while(frames != None):
        # Retrieves mic volume input
        f = open(sound_FILE, "r")    # Open 'deepfry_volume.txt' file in 'read mode'
        try:
            volume = f.readlines()[0]   # Tries to read the first line (lastest mic input volume)
            volume = volume.strip()     # Strips EOL characters from mic input volume (as a string)
        except:
            print("ERROR: VOLUME READ FAILURE")    # If no value retrieved, print error 
        f.close()

        volume = float(volume)          # Converts mic input value from str to float value
        if volume < 1:  volume = 1      # If mic input value is < 1, set = 1
        #print(volume)                  # Print mic input value

        # Increases the saturation of frame by mic input value (volume) 
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1] * volume
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        frame = cv2.resize(frame, (1280, 720))          # Resize frame
        cv2.imshow('Project - Deepfry', frame)          # Display frame
        frame = frames.__next__()                       # Grab next frame

        if cv2.waitKey(10) == 27:           # Check if 'Esc' was hit
            print("\nEXITING...")
            stream.stop()                   # if so, stop Audio Stream and exit program
            return

    # RESTART the video if the end is reached
    print("\nRESTART...\n")
    vidLoop(filename)


# FUNCTION that processes the volumn input data
#   Input: the mic input data for volumn
def frame_callback(indata, frames, time, status):
    sensitivity = 10    # Determines the sensitivity of input volume
                        # If you wanna change the sensitivity of the program,
                        # Change this varible. 10 is default

    # Takes the incoming data (indata) and converts it to volume data
    volume_norm = np.linalg.norm(indata) * sensitivity

    f = open(sound_FILE, "r+")                  # Open 'deepfry_volume.txt' in 'write mode'         
    f.write(str(volume_norm))                   # Stores volume data in file
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

    # Creates window
    cv2.namedWindow('Project - Deepfry', cv2.WINDOW_NORMAL)

    # Loops Video
    print("\tPLAYING VIDEO...\n")
    print("\tTo exit the program, press 'ESC' on the second window")
    vidLoop(filename)
    
    # Destorys all windows
    cv2.destroyAllWindows()
