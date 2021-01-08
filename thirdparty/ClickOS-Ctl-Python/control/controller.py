# -*- coding: utf-8 -*-
from .version import __version__
from .errors import Error
from .commech import ComMechanism
from .xenstore import XenStore
import logging

class MechanismError(Error):
  def __init__(self, message):
    super().__init__(
      title="mechanism error",
      message=message
    )

class NoFileError(Error):
  def __init__(self, file_name):
    super().__init__(
      title="file not found",
      message="file with name [{}] could not be opened".format(file_name)
    )

class UnimonControl():

  VERSION = "0.01"
  DEFAULT_COM_MECH="xenstore"

  COMMUNICATION_MECHANISMS = {
    "xenstore": XenStore
  }

  def __init__(self):
    self.logger = logging.getLogger("unimon-control")

### OUTPUT CONTROL

  def __error(self, message):
    """ Formats and outputs errors to the logger """
    self.logger.error("🆘  || {}".format(message))
    return None, message

  def messgage(self, message, data=None, logger=None):
    message = "💬  || {} || data: {}".format(message, data)
    if not logger:
      logger = self.logger
    logger.debug(message)
    return data, None

###

### PUBLIC METHODS
  def set_debug(self):
    self.logger.setLevel(logging.DEBUG)

  def get_version(self):
    """ returns the unimon ctl version """
    return __version__

  def get_router_list(self, mechanism, domain_id):
    """ gets the current state of a clickos router """
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    routers = mechanism.get_router_list(domain_id)
    return routers

  def get_router_state(self, mechanism, domain_id, router_id):
    """ gets the current state of a clickos router """
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    router_state = mechanism.get_router_state(domain_id, router_id)
    return router_state

  def install_from_file(self, mechanism, domain_id, config_path, config_name):
    """ install a click config to a clickos doamin from a .click file """
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    config = ""
    try:
      with open(config_path, 'r') as config_file:
        config = config_file.read()
    except:
      raise NoFileError(config_path)
    return mechanism.install_click_config(domain_id, config, config_name)
  
  def start_router(self, mechanism, domain_id, router_id):
    """ starts a click router on a target clickos domain """
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    rid = mechanism.start_router(domain_id, router_id)
    return rid

  def stop_router(self, mechanism, domain_id, router_id):
    """ stops a click router on a target clickos domain """
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    rid = mechanism.stop_router(domain_id, router_id)
    return rid

  def remove_router(self, mechanism, domain_id, router_id, force):
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    mechanism.remove_router(domain_id, router_id, force)
    return

  def get_elem_handler(self, mechanism, domain_id, router_id, element_name, handler_name):
    mechanism = self.__validate_mechanism(mechanism, domain_id)
    return mechanism.get_element_handler(domain_id, router_id, element_name, handler_name)

### PRIVATE METHODS

  def __validate_mechanism(self, mech_name, dom_id):
    mech_name = mech_name.lower()
    if not mech_name in self.COMMUNICATION_MECHANISMS:
      raise MechanismError("invalid communication mechanism given")
    mech = self.COMMUNICATION_MECHANISMS.get(mech_name)(self.logger.level, mech_name, self.messgage)
    mech.test(dom_id)
    return mech