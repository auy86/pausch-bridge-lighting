import numpy as np
import matplotlib.cm
import rpbtools
import random


plasma = matplotlib.cm.get_cmap('plasma')
hsv = matplotlib.cm.get_cmap('hsv')


# phase 1
frames1 = [np.zeros((2,228,3))]

rainbow = hsv(np.arange(8)/8)[:,:3]

for i in range(224):
  reshaped_rainbow = np.roll(rainbow, i).reshape((2,4,3))
  bg = np.zeros((2,228,3))
  bg[:,i:i+4,:] = reshaped_rainbow
  lastidx = len(frames1) - 1
  fade = np.linspace(0,1,8)
  for j in range(8):
    frames1.append(frames1[lastidx]*(1-fade[j]) + bg*fade[j])

frames1 = np.array(frames1[1:])

for i in range(17):
  #color = np.array(plasma(i/17)[:3])
  #color = color*0.75+0.25
  color = hsv(i/17)[:3]
  fade = np.linspace(1,0,32*6)
  frames1[i*32*3:(i+2)*32*3, :, i*3*4:(i*3+1)*4, :] = np.outer(fade, color)[:,np.newaxis,np.newaxis,:]


# phase 2
with open('pi_digits.txt', 'r') as file:
  digits = file.read()
digits = digits[2:]
digits = np.array(list(map(int, digits[:57])))[::-1]

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


# phase 3

with open('pi_digits.txt', 'r') as file:
  digits = file.read()
digits = digits[2:]
digits = list(map(int, digits[:57*100]))
digits = np.array(digits).reshape((100,57))
colorbg = plasma(digits/9)[:,:,:3]
colorbg = np.repeat(colorbg, 2, axis=0)


sinemask = (np.sin(np.linspace(0,14*np.pi,228))+1)/2
intensity = (np.cos(np.linspace(0,9*np.pi,32*30))+1)/2

frames3 = []

firstdestination = sinemask[np.newaxis,:,np.newaxis] * frames2[-1]
for i in range(3*32):
  frames3.append(frames2[-1] * (1-i/96) + firstdestination * i/96)

for i in range(32*30):
  bg = colorbg[i//80] * (1-(i%80)/80) + colorbg[i//80+1] * ((i%80)/80)
  bg = np.repeat(np.repeat(bg[np.newaxis,...], 4, axis=1), 2, axis=0)
  mask = sinemask * intensity[i]
  frames3.append(bg*mask[np.newaxis,:,np.newaxis])

frames3 = np.array(frames3)


# phase 4

frames4 = np.zeros((1,57,3))
numbers = list(map(int, '3141592653'))

curridx = 8
for i in range(10):
  repeating = frames4[-1]
  newbigsegment = np.repeat(frames4[-1:], 100, axis=0)
  color = np.array(hsv(i/10)[:3])
  for j in range(numbers[i]):
    start = int(j/numbers[i]*32)
    end = int((j+1)/numbers[i]*32)
    newbigsegment[64+start:64+end, curridx+j] = np.outer(np.linspace(0,1,end-start), color)
    newbigsegment[64+end:, curridx+j] = color
  curridx += numbers[i] + 1
  frames4 = np.concatenate((frames4, newbigsegment), axis=0)

frames4 = np.repeat(np.repeat(frames4[:,np.newaxis,:,:], 4, axis=2), 2, axis=1)


# final lingering and fade

frames5_1 = np.repeat(frames4[-1:], 5*32, axis=0)
frames5_2 = np.einsum('a,bcd->abcd', np.linspace(1,0,5*32), frames4[-1])
frames5_3 = np.zeros((3*32,2,228,3))
frames5 = np.concatenate((frames5_1, frames5_2, frames5_3), axis=0)


# combine

frames = np.concatenate((frames1, frames2, frames3, frames4, frames5), axis=0)


# convert to video
video = rpbtools.array2video(frames)
rpbtools.visualize_video(video)
rpbtools.save_video('pi_allparts.avi', video)

