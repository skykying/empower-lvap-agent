from .commech import CommMechanism

import logging

class Router():

  MAX_NAME_LEN = 32

  ROUTER_STATES = [
    "Unknown",
    "Running",
    "Stopped",
    "Error"
  ]

  def __init__(self, name, com_mech, dom_id, config, router_id=None, state=None):
    self.name = name
    self.com_mech = com_mech
    self.dom_id = dom_id if isinstance(dom_id, int) else 0
    self.config = config
    self.state=(state or self.ROUTER_STATES[0])
    self.router_id = router_id
    if not router_id:
      self.router_id = self.com_mech.get_next_rid(self.dom_id)
    if not self.__valid_config():
      logging.error("!! router created with invalid config !!")
      raise Exception
    if not self.com_mech.test(self.dom_id):
      logging.error("!! router communications test failed !!")
      raise Exception
    
    self.print_info()

  def __valid_config(self):
    ''' dont look here, pls '''
    if not isinstance(self.name, str):
      return False
    if len(self.name) > self.MAX_NAME_LEN:
      return False
    if not isinstance(self.com_mech, CommMechanism):
      return False
    if not isinstance(self.dom_id, int):
      return False
    if self.dom_id < 1:
      return False
    if not isinstance(self.router_id, int):
      return False
    if self.router_id < 0:
      return False
    if not isinstance(self.config, str):
      return False
    return True

  def __get_next_id(self):
    rid = self.com_mech.get_next_rid(self.dom_id)
    if rid > -1:
      return rid
    logging.error("failed to get next router id [domain {}]".format(self.dom_id))
    raise Exception

  def print_info(self):
    logging.debug("router | {}".format(self.name))
    if not self.__valid_config():
      logging.debug(" - has invalid config!")
      return
    logging.debug("~~~~~")
    logging.debug("router | {}".format(self.name))
    logging.debug(" - communication mech | {}".format(self.com_mech.get_type_name()))
    logging.debug(" - xen domain id | {}".format(self.dom_id))
    logging.debug(" - clickos router id | {}".format(self.router_id))
    logging.debug(" - router state | {}".format(self.state))
    logging.debug("~~~~~")

  def get_state(self):
    state = self.com_mech.get_router_state(self.dom_id, self.router_id)
    if not state:
      self.state = self.ROUTER_STATES[0]
    else:
      self.state = state
    return self.state

