import numpy as np
import matplotlib.cm
import rpbtools


plasma = matplotlib.cm.get_cmap('plasma')
hsv = matplotlib.cm.get_cmap('hsv')




# phase 1
frames = []

rainbow = hsv(np.arange(8)/8)[:,:3]

for i in range(224):
  reshaped_rainbow = np.roll(rainbow, i).reshape((2,4,3))
  bg = np.zeros((2,228,3))
  bg[:,i:i+4,:] = reshaped_rainbow
  for _ in range(8):
    frames.append(bg.copy())

frames = np.array(frames)

for i in range(18):
  color = np.array(plasma(i/19)[:3])
  color = color*0.5+0.5
  fade = np.linspace(1,0,32*3)
  frames[i*96:(i+1)*96, :, i*3*4:(i*3+1)*4, :] = np.outer(fade, color)[:,np.newaxis,np.newaxis,:]






# convert to video
video = rpbtools.array2video(frames)
rpbtools.save_video('test.avi', video)

import pdb
pdb.set_trace()



