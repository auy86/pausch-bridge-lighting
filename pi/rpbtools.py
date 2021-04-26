import numpy as np
import cv2


def array2video(frames):
  assert(frames.shape[1:] == (2,228,3))
  numframes = len(frames)

  video = np.zeros((numframes, 8, 228, 3))

  for i in range(len(frames)):
    for b in range(57):
      topseq = frames[i,0,b*4:(b+1)*4,:]
      bottomseq = frames[i,1,b*4:(b+1)*4,:]

      video[i,0,b*4:(b+1)*4,:] = topseq
      video[i,0:4,b*4+1,:] = np.roll(topseq, -1, axis=0)

      video[i,7,b*4:(b+1)*4,:] = bottomseq
      video[i,4:8,b*4+1,:] = np.roll(bottomseq, -1, axis=0)

  mask = cv2.cvtColor(cv2.imread('mask.png'), cv2.COLOR_BGR2RGB)
  mask = (mask[np.newaxis, :, :] != 0)
  video *= mask

  return video





def visualize_video(video):
  pass



def save_video(name, video):
  fourcc = cv2.VideoWriter_fourcc(*'png ')
  writer = cv2.VideoWriter(name, fourcc, 30, (228,8))
  video = (video*255).astype(np.uint8)
  for frame in video:
    writer.write(frame[...,::-1])
  writer.release()
