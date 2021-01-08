# -*- coding: utf-8 -*-
from .errors import Error
from .utility import inform
import logging

class ComMechNoOpError(Error):

  def __init__(self, name):
    message = "communication mechanism [{}] does not support this".format(name)
    super().__init__(message=message)
    self.title = "Communication Mechanism Error"

class InvalidDomainError(Error):

  def __init__(self, dom_id):
    super().__init__(
      title="domain not found",
      message="this domain [{}] could not be found".format(dom_id),
      code=400
    )

class NonClickOSDomError(Error):

  def __init__(self, dom_id):
    super().__init__(
      title="domain not clickos",
      message="domain [{}] could not be identified as a clickos domain".format(dom_id),
      code=400
    )

class RouterStillRunningError(Error):

  def __init__(self, dom_id, rid):
    super().__init__(
      title="router already running",
      message="router [{}] is still running on domain [{}]".format(rid, dom_id),
      code=400
    )

class StateChangeError(Error):

  def __init__(self, rid, reason):
    super().__init__(
      title="state change error",
      message="could not set the routers state || reason: {}".format(reason),
      code=400
    )

class ComMechanism():

  ROUTER_STATUS = {
    "unknown": "Unknown",
    "running": "Running",
    "stopped": "Halted",
    "error": "Error"
  }

  def __init__(self, log_level, name, message_func):
    self.name = name
    self.message_func = message_func
    self.logger = logging.getLogger(name)
    self.logger.setLevel(log_level)
    inform(self.logger, "communication mechanism: {}".format(self.name))

  def test(self, dom_id):
    return False

  def get_type_name(self):
    ''' returns the name of the mech type '''
    return name

  def get_router_list(self, dom_id):
    raise ComMechNoOpError(self.name)

  def get_router_state(self, dom_id, router_id):
    raise ComMechNoOpError(self.name)

  def get_next_rid(self, dom_id):
    raise ComMechNoOpError(self.name)

  def install_click_config(self, dom_id, config, name):
    ''' returns a router id on success, -1 on fail '''
    raise ComMechNoOpError(self.name)

  def start_router(self, dom_id, router_id):
    ''' starts a router of a given id '''
    raise ComMechNoOpError(self.name)

  def stop_router(self, dom_id, router_id):
    ''' stops a router of a given id '''
    raise ComMechNoOpError(self.name)

  def remove_router(self, dom_id, router_id, force):
    raise ComMechNoOpError(self.name)

  def get_element_handler(self, dom_id, rid, element_name, handler_name):
    raise ComMechNoOpError(self.name)
