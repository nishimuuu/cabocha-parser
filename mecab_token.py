# -*-coding: utf-8 -*-
__author__ = 'nishimuuu'
# write code here...
class MeCabToken:
  def __init__(self, surface, feature):
    self.word =  surface
    features = feature.split(',')
    error_cnt = 0
    try:
      self.surface_length = len(surface)
      self.pos = features[0]
      self.pos_detail = features[1]
      self.pos_detail2 = features[2]
      self.pos_detail3 = features[3]
      self.conjugate = features[4]
      self.conjugate_fmt = features[5]
      self.surface_base = features[6]
      if self.surface_length >= 7:
        self.reading = features[7]
        self.pronounce = features[8]
    except IndexError:
      error_cnt += 1

    if not error_cnt <= 1:
      print 'parse finish. error: ' + str(error_cnt)


  def get(self, method='word'):
      method_name = 'get_{}'.format(method)
      if hasattr(self, method_name):
          return getattr(self, method_name)().decode('utf-8')
      else:
          return None

  def get_word(self):
    return self.word

  def get_pos(self):
    return self.pos

  def get_pos_detail(self):
    return self.pos_detail

  def get_pos_detail2(self):
    return self.pos_detail2

  def get_pos_detail3(self):
    return self.pos_detail3

  def get_conjugate(self):
    return self.conjugate

  def get_conjugate_fmt(self):
    return self.conjugate_fmt

  def get_surface_base(self):
    return self.surface_base

  # def get_reading(self):
  #   return self.reading
  #
  # def get_pronounce(self):
  #   return self.pronounce

  def get_surface_length(self):
    return self.surface_length
