#!/usr/bin/env python3
# pb_color_bars.py: demonstration of generating video content using OpenCV

# This script assumes the availability of the OpenCV and numpy libraries. A
# recommended method for installing these in Python 3 follows:
#
#   pip3 install opencv-contrib-python
#
# General OpenCV information:   https://opencv.org/
# General NumPy information:    https://numpy.org/

#================================================================
# Import standard Python modules.
import argparse
import math

# Import the numpy and OpenCV modules.
import numpy as np
import cv2 as cv

#================================================================
# Define the video properties using the canonical video format for the Pausch
# Bridge lighting system.
frame_rate   = 30
frame_width  = 228
frame_height = 8

# Specify a format code and file format.  The exact combinations of codec and
# file formats available are different for each platform.
codec_code = cv.VideoWriter.fourcc(*'png ') # PNG images, lossless, clean block edges
file_extension = 'avi'

#================================================================
# Define a set of colors as (B,G,R) triples of unsigned 8-bit integers.

colors = ((255,255,255),      # white
          (65,65,255),     # red
          (31,147,255),     # orange
          (31,192,255),      # yellow
          (82,233,23),     # green
          (233,174,23),     # blue
          (233,23,116),     # purple
          (199,23,233),     # pink
          )



#================================================================
# Generate successive frames of the video sequence.

def isSquare(x):
  return (math.isqrt(x) ** 2 == x)

def frame_generator(verbose, tempo):
    count = 0             # count of generated frames
    frame_time = 0.0      # time stamp for generated frame in seconds
    keyframe_phase = 0.0  # unit phase for the cross-fade, cycles over 0 to 1

    frame_interval = 1.0 / frame_rate                       # seconds between video frames
    keyframe_interval = 7.0 / tempo                        # seconds between key frames
    keyframe_rate = 1.0 / (frame_rate * keyframe_interval)  # phase / frame

    # Generate two frames to use as keyframes.
    frame0 = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    # frame1[:,4:20,:] = colors[0]

    # Fill the frames with the first two colors.
   
    frame0[:] = colors[0]
    frame0[:,0:32,:] = colors[1]
    frame1 = frame0
    frame1[:,32:36,:] = colors[1]
    square = 1
    offset = 32
    squared = False
    pause = 0
    
    while True:
        # Cross-fade between successive key frames at the given tempo.  This will
        # return a new frame of integer pixels.
        frame = cv.addWeighted(frame0, (1.0 - keyframe_phase), frame1, keyframe_phase, 0.0)

        # Advance the cross-fade phase.
        keyframe_phase += keyframe_rate

        # Once the second keyframe is reached, generate the successor and reset the fade.
        if keyframe_phase >= 1.0:
            keyframe_phase -= 1.0
            if (squared):
              pause -= 1
              if (pause == 0):
                frame0 = frame1
                squared = False
                square += 1
                frame1[:,offset:offset+4,:] = colors[square % 8]
            elif (isSquare(count+2)):
              frame0 = frame1
              # frame1[:,0:offset+4,:] = colors[0]
              count += 1
              offset += 4
              squared = True
              pause = 10
            else:
              frame0 = frame1
              frame1[:,offset+4:offset+8,:] = colors[square % 8]
              count += 1
              offset += 4 
        
        # Return the frame and advance the generator state.
        yield frame
        frame_time += frame_interval


blank = ((0,0,0))
def end_transition(verbose, input, lastframe, tempo):
    count = 0                  # count of generated frames
    frame_time = 0.0           # time stamp for generated frame in seconds
    keyframe_phase = 0.0       # unit phase for the cross-fade, cycles over 0 to 1
    fibonacci_sequence = [0,1] # for generating fibonacci number
    width_generated = 0        # for tracking width generated

    frame_interval = 1.0 / frame_rate                       # seconds between video frames
    keyframe_interval = 60.0 / tempo                        # seconds between key frames
    keyframe_rate = 1.0 / (frame_rate * keyframe_interval)  # phase / frame

    blank_main = np.array(blank,dtype=np.uint8).reshape((1,1,3))
    blank_bars = cv.resize(blank_main, None, fx=4, fy=8, interpolation=cv.INTER_NEAREST)

    # Generate Frame 1 (blank)

    bars_width = blank_bars.shape[1]
    copies = (frame_width + bars_width) // bars_width   
    large = np.tile(blank_bars, (1,copies,1))

    frame0 = lastframe[0:frame_height, 0:frame_width, :]
    frame1 = large[0:frame_height, 0:frame_width, :]
    
    while True:
        # Cross-fade between successive key frames at the given tempo.  This will
        # return a new frame of integer pixels.
        frame = cv.addWeighted(frame0, (1.0 - keyframe_phase), frame1, keyframe_phase, 0.0)

        # Advance the cross-fade phase.
        keyframe_rate = 1 / (5 * frame_rate)
        keyframe_phase += keyframe_rate

        # Once keyframe is reached, return null.
        if keyframe_phase >= 1.0:
            yield
        
        # Return the frame and advance the generator state.
        yield frame
        count += 1
        frame_time += frame_interval

#================================================================
# Write a video file in the default format.

def write_video_file(basename, length, verbose, *args):

    # Open the writer with a path, format, frame rate, and size.
    filename = basename + '.' + file_extension
    out = cv.VideoWriter(filename, codec_code, frame_rate, (frame_width, frame_height))

    if verbose:
        print(f"Open file {filename} for output.")

    # Set up the frame generator.
    frame_sequence = frame_generator(verbose, *args)

    # Synthesize some frames and write them to the stream.
    for count in range(length):
        out.write(next(frame_sequence))

    #Adding End Transition
    end_sequence = end_transition(verbose, input, next(frame_sequence), *args)

    while True:
        next_frame = next(end_sequence)
        if next_frame is None:
            break
        else:
            out.write(next_frame)

    # Release everything when done.
    out.release()

#================================================================
# Main script follows.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = """Perfect square video generator for the Pausch Bridge.""")
    parser.add_argument( '-v', '--verbose', action='store_true', help='Enable more detailed output.' )
    parser.add_argument( '-l', '--length', type=int, default=1200, help='Number of frames to generate (at 30 fps)')
    parser.add_argument( '-t', '--tempo', type=float, default=30.0, help='Tempo of key frames in beats per minute.')
    parser.add_argument( 'basename', default='perfect_squares_part2', nargs='?', help='Base name of output file (not including .mp4 extension).')

    args = parser.parse_args()
    write_video_file(args.basename, args.length, args.verbose, args.tempo)