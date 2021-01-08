# -*- coding: utf-8 -*-
import json

'''
TODO:
 - comment
 - check pep8
'''

class Error(Exception):

  EMOJI = '‼️'

  def __init__(self, title="error", message="unimon-ctl encouted an error with no description", code=500):
    super().__init__(message)
    self.title = title
    self.message = message
    self.code = code

  def get_pretty(self):
    message = "{}  || {} || {}".format(self.EMOJI, self.title, self.message)
    return message

  def get_json(self):
    error = {
      "error": self.title,
      "message": self.message
    }
    return json.dumps(error), self.code
