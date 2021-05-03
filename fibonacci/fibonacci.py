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
colors = ((0,0,0),       # black
          (255,0,0),     # blue
          (255,255,0),   # cyan
          (0,255,0),     # green
          (0,255,255),   # yellow
          (0,0,255),     # red
          (255,0,255),   # magenta
          (255,255,255), # white
          )

main_color = ((0,165,255))

blank = ((0,0,0))
#================================================================
def getimgcolor(img_file):
    image = cv.imread(img_file, flags=cv.IMREAD_COLOR)
    image_width_buffer = image.shape[1] // (58)
    image_height_buffer = image.shape[0] // 14

    colors = []

    for i in range(13):
        color_space = []
        for j in range(57):
            average_color_row = np.average(image[i*image_height_buffer:(i+1)*image_height_buffer, j*image_width_buffer:(j+1)*image_width_buffer], axis=0)
            average_color = np.average(average_color_row, axis = 0)
            #color_space.append(image[i*image_height_buffer][j*image_width_buffer])
            color_space.append(average_color)
        colors.append(color_space)
            

    return colors

#================================================================
# Generate color tiles based on image color

def generate_bkg(colors, row, start, tiles):
    small_tile = np.array(colors[row][start],dtype=np.uint8).reshape((1,1,3))
    bars_tile = cv.resize(small_tile, None, fx=4, fy=8, interpolation=cv.INTER_NEAREST)
    if (tiles == 1):
        return bars_tile
    else:
        return np.concatenate((generate_bkg(colors, row, (start + 1), tiles - 1),bars_tile),axis=1)

# Generate successive frames of the video sequence.

def frame_generator(verbose, input, tempo):
    count = 0                  # count of generated frames
    frame_time = 0.0           # time stamp for generated frame in seconds
    keyframe_phase = 0.0       # unit phase for the cross-fade, cycles over 0 to 1
    fibonacci_sequence = [0,1] # for generating fibonacci number
    width_generated = 0        # for tracking width generated

    frame_interval = 1.0 / frame_rate                       # seconds between video frames
    keyframe_interval = 60.0 / tempo                        # seconds between key frames
    keyframe_rate = 1.0 / (frame_rate * keyframe_interval)  # phase / frame

    #Get colors from image
    colors = getimgcolor(input)
    
    # Generate a set of color bars aligned with 4x8 pixel blocks.
    # small = np.array(colors,dtype=np.uint8).reshape((1,len(colors),3))
    # bars = cv.resize(small, None, fx=4, fy=8, interpolation=cv.INTER_NEAREST)

    #generate main tile representing fibonacci number

    small_main = np.array(main_color,dtype=np.uint8).reshape((1,1,3))
    bars_main = cv.resize(small_main, None, fx=4, fy=8, interpolation=cv.INTER_NEAREST)

    #small_bkg = np.array(blank,dtype=np.uint8).reshape((1,1,3))
    #bars_bkg = cv.resize(small_bkg, None, fx=4, fy=8, interpolation=cv.INTER_NEAREST)

    # Generate Frame 0 (blank)

    background_count = (frame_width // bars_main.shape[1])
    #frame0_reference = np.tile(bars_bkg, (1,background_count,1))
    frame0_reference = generate_bkg(colors, 0, 0, background_count)

    # Generate an output frame by tiling it with the bars.
    #bars_width = bars.shape[1]
    bars_width = bars_main.shape[1]
    copies = (frame_width + bars_width) // bars_width
    #copies = frame_width // bars_width
    #large = np.tile(bars, (1,copies,1))

    generated = 0
    offset = generate_bkg(colors, 1, 0, 8)
    generating = bars_main
    width_generated = width_generated + bars_main.shape[1]
    background_count = ((frame_width - width_generated) // bars_width)
    #background = np.tile(bars_bkg, (1,background_count,1))
    background = generate_bkg(colors, 1, 0, background_count)

    #large = np.concatenate((generated,generating,background),axis=1)
    large = np.concatenate((offset,generating,background),axis=1)

    generated = generating

    # Select slices of the full frame to use as initial key frames.
    #frame0 = large[0:frame_height, 0:frame_width, :]
    #frame1 = large[0:frame_height, 4:frame_width+4, :]
    frame0 = frame0_reference[0:frame_height, 0:frame_width, :]
    frame1 = large[0:frame_height, 0:frame_width, :]
    #next_offset = 8

    # Write out the first frames for debugging.
    #cv.imwrite("color_bars_frame0.png", frame0)
    #cv.imwrite("color_bars_frame1.png", frame1)

    row_count = 2
    
    while True:
        # Cross-fade between successive key frames at the given tempo.  This will
        # return a new frame of integer pixels.
        frame = cv.addWeighted(frame0, (1.0 - keyframe_phase), frame1, keyframe_phase, 0.0)

        # Advance the cross-fade phase.
        keyframe_rate = 1 / (0.7 * fibonacci_sequence[-1] * frame_rate)
        keyframe_phase += keyframe_rate

        # Once the second keyframe is reached, generate the successor and reset the fade.
        if keyframe_phase >= 1.0:
            keyframe_phase -= 1.0
            frame0 = frame1
            #frame1 = large[0:frame_height, next_offset:frame_width+next_offset, :]
            #next_offset = (next_offset + 4) % bars_width
            offset = generate_bkg(colors, row_count, 0, 8)
            start_count = 9
            large = np.concatenate((offset,bars_main),axis=1)
            for i in range(1,len(fibonacci_sequence)):
                #space = np.tile(bars_bkg, (1,fibonacci_sequence[i],1))
                space = generate_bkg(colors, row_count, start_count, fibonacci_sequence[i])
                start_count += fibonacci_sequence[i]
                large = np.concatenate((large,space,bars_main),axis=1)

            width_generated = large.shape[1]
            
            #generating_space = np.tile(bars_bkg, (1,fibonacci_sequence[-1],1))
            #generating = np.concatenate((generating_space,bars_main),axis=1)
            #width_generated = width_generated + generating.shape[1]
            

            background_count = ((frame_width - width_generated) // bars_width)
            if (background_count > 0):
                background = generate_bkg(colors, row_count, start_count, background_count)
                start_count += background_count
                large = np.concatenate((large,background),axis=1)

            #background_count = 0
            #background = np.tile(bars_bkg, (1,background_count,1))
            #background = generate_bkg(colors, row_count, start_count, background_count)


            #large = np.concatenate((generated,generating,background),axis=1)        # Combine generated, generating and background
            #generated = np.concatenate((generated,generating),axis=1)               # Update array containing generated portions
            
            frame1 = large[0:frame_height, 0:frame_width, :]

            # Update Fibonacci
            fibonacci_sequence.append(fibonacci_sequence[-1] + fibonacci_sequence[-2])

            row_count += 1 #update row count
        
        offset_count = 32

        for i in range(1,len(fibonacci_sequence)):
            frame[0:8, offset_count:offset_count + 4, 0:4] = bars_main
            offset_count += (4 + fibonacci_sequence[i]*4)
        
        # Return the frame and advance the generator state.
        yield frame
        count += 1
        frame_time += frame_interval

#================================================================
def start_transition(verbose, input, lastframe, tempo):
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

    # Generate Frame 0 (blank)

    bars_width = blank_bars.shape[1]
    copies = (frame_width + bars_width) // bars_width
    large = np.tile(blank_bars, (1,copies,1))

    frame0 = large[0:frame_height, 0:frame_width, :]
    frame1 = lastframe[0:frame_height, 0:frame_width, :]
    
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

def write_video_file(basename, length, verbose, input, *args):

    # Open the writer with a path, format, frame rate, and size.
    filename = basename + '.' + file_extension
    out = cv.VideoWriter(filename, codec_code, frame_rate, (frame_width, frame_height))

    if verbose:
        print(f"Open file {filename} for output.")

    # Set up the frame generator.
    frame_sequence = frame_generator(verbose, input, *args)

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
    parser = argparse.ArgumentParser(description = """Color bar video generator for the Pausch Bridge.""")
    parser.add_argument( '-v', '--verbose', action='store_true', help='Enable more detailed output.' )
    parser.add_argument( '-l', '--length', type=int, default=480, help='Number of frames to generate (at 30 fps)')
    parser.add_argument( '-t', '--tempo', type=float, default=30.0, help='Tempo of key frames in beats per minute.')
    parser.add_argument( 'basename', default='fibonacci', nargs='?', help='Base name of output file (not including .mp4 extension).')
    parser.add_argument( '-i', '--input', required=True, help='Name of input image')

    args = parser.parse_args()
    write_video_file(args.basename, args.length, args.verbose, args.input, args.tempo)