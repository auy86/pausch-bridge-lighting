import numpy as np

class Bridge:

  def __init__(self):
    self.panels = []
    self.panels.extend(self.initWithStr('h2'*4)) # brickwall
    self.panels.extend(self.initWithStr('h3')) # diagwall
    self.panels.extend(self.initWithStr('v8'*3)) # verticals
    self.panels.extend(self.initWithStr('h4h3v5')) # slopedrails
    self.panels.extend(self.initWithStr('h3'+('h4'*35)+'h3')) # mainspan
    self.panels.extend(self.initWithStr('v5'+('h4'*6)+'h2v8')) # purnellend
    self.startindices = {}
    self.startindices['brickwall'] = 0
    self.startindices['diagwall'] = 4
    self.startindices['verticals'] = 5
    self.startindices['slopedrails'] = 8
    self.startindices['mainspan'] = 11
    self.startindices['purnellend'] = 48

  def initWithStr(self, initstr):
    reslist = []
    for i in range(len(initstr)//2):
      d = initstr[i*2]
      l = initstr[i*2+1]
      d = 'horizontal' if d == 'h' else 'vertical'
      l = int(l)
      reslist.append(Panel(direction=d, length=l))
    return reslist

  def getMapping(self):
    panelmappings = []
    for p in self.panels:
      panelmappings.append(p.getPanelMapping())
    return np.concatenate(panelmappings, axis=1)


class Panel:

  '''
  @param direction: Each panel can be categorized as having lights laid out
                    either horizontally or vertically.

  @param length: IF direction == 'horizontal', then there are two groups of
                 lighting fixtures across the top and bottom of same length.
                 length refers to the length of one of them. Valid range: {2,3,4}

                 ELSE IF direction == 'vertical', then there are two groups
                 of lighting fixtures stacked vertically that can vary in length.
                 length refers to the length of BOTH of them concatenated.
                 Valid range: {5,8}

  If direction == 'horizontal', then values are stored left to right.
  If direction == 'vertical', then values are stored top to bottom.
  '''
  def __init__(self, direction='horizontal', length=4):
    self.direction = direction
    self.length = length

    if self.direction == 'horizontal':
      if length not in [2,3,4]:
        raise ValueError('Invalid horizontal length')
      self.toplights = np.full((length, 3), 255, dtype='uint8')
      self.bottomlights = np.full((length, 3), 255, dtype='uint8')

    elif self.direction == 'vertical':
      if length not in [5,8]:
        raise ValueError('Invalid vertical length')
      self.vertlights = np.full((length, 3), 255, dtype='uint8')

    else:
      raise ValueError('Invalid direction')


  def setPanelColor(self, rgb):
    if self.direction == 'horizontal':
      self.toplights[:] = rgb
      self.bottomlights[:] = rgb
    else:
      self.vertlights[:] = rgb

  '''
  @param side: Use side=None for vertical panels, side='top' for
               the top bar of a horizontal panel, and side'bottom'
               for the bottom bar.
  '''
  def setPixel(self, index, rgb, side=None):
    if (self.direction == 'vertical' and side is not None) or \
       (self.direction == 'horizontal' and side not in ['top', 'bottom']):
       raise ValueError('Invalid side {} for panel type {}'.format(side, self.direction))

    if side is None:
      self.vertlights[index] = rgb
    elif side == 'top':
      self.toplights[index] = rgb
    else:
      self.bottomlights[index] = rgb


  def getPanelMapping(self):
    result = np.zeros((8,4,3), dtype='uint8')
    if self.direction == 'horizontal':
      result[0,:self.length] = self.toplights
      result[7,:self.length] = self.bottomlights
    else:
      if self.length == 8:
        result[:,1] = self.vertlights
      else:
        result[1:4,1] = self.vertlights[:3]
        result[5:7,1] = self.vertlights[3:]
    return result


if __name__ == '__main__': # testing
  b = Bridge()
  assert(len(b.panels) == 57)
  pixelmapping = b.getMapping()
  assert(pixelmapping.shape == (8,228,3))
  assert(pixelmapping.dtype == np.uint8)
  assert(np.sum(pixelmapping) == 422*3*255)

  b.panels[0].setPixel(0,(1,1,1),side='top')
  b.panels[b.startindices['verticals']].setPixel(1,(1,1,1),side=None)
  b.panels[30].setPixel(3,(1,1,1),side='bottom')
  b.panels[b.startindices['purnellend']].setPixel(4,(1,1,1))
  assert(np.sum(b.getMapping()) == 12+418*3*255)

  print('Basic tests passed')
