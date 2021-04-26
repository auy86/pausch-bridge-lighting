import numpy as np
import matplotlib.cm
import rpbtools


plasma = matplotlib.cm.get_cmap('plasma')
hsv = matplotlib.cm.get_cmap('hsv')


# phase 1
frames1 = []

rainbow = hsv(np.arange(8)/8)[:,:3]

for i in range(224):
  reshaped_rainbow = np.roll(rainbow, i).reshape((2,4,3))
  bg = np.zeros((2,228,3))
  bg[:,i:i+4,:] = reshaped_rainbow
  for _ in range(8):
    frames1.append(bg.copy())

frames1 = np.array(frames1)

for i in range(18):
  color = np.array(plasma(i/19)[:3])
  color = color*0.75+0.25
  fade = np.linspace(1,0,32*3)
  frames1[i*96:(i+1)*96, :, i*3*4:(i*3+1)*4, :] = np.outer(fade, color)[:,np.newaxis,np.newaxis,:]


# phase 2
with open('pi_digits.txt', 'r') as file:
  digits = file.read()
digits = digits[2:]
digits = np.array(list(map(int, digits[:57])))

colors = plasma(np.linspace(0,1,10))[:,:3]

frames2 = np.zeros((32*57,57,3))

for i in range(57):
  d = digits[i]

  # fading
  fade = np.linspace(0,1,32)
  colorfade = np.outer(fade, colors[d])
  frames2[i*32:(i+1)*32,56-i,:] = colorfade

  #persistence
  frames2[(i+1)*32:,56-i,:] = colors[d]

frames2 = np.tile(np.repeat(frames2, 4, axis=1)[:,np.newaxis,:,:], (1,2,1,1))
print(frames2.shape)



# combine

frames = np.concatenate((frames1, frames2), axis=0)


# convert to video
video = rpbtools.array2video(frames)
rpbtools.save_video('test.avi', video)

