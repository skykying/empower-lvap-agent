# -*- coding: utf-8 -*-
from .commech import ComMechanism, InvalidDomainError, NonClickOSDomError, RouterStillRunningError, StateChangeError
from .utility import inform, success
from .errors import Error
try:
  from pyxs import Client as PyXSClient
  from pyxs import PyXSError, InvalidPath
except:
  print("🆘  || unimon-ctl requires the pyxs package for xenstore communication")
import logging
import os
import time

class XenStoreConnectError(Error):

  def __init__(self, extra=""):
    super().__init__(
      title="xenstore connection failure",
      message="failed to connect to the xenstore || information: {}".format(extra)
    )

class XenStoreWriteError(Error):

  def __init__(self, transaction_id):
    super().__init__(
      title="xenstore write failure",
      message="could not write data to xenstore in transaction [{}]".format(transaction_id)
    )

class XenStoreReadError(Error):

  def __init__(self, path):
    super().__init__(
      title="xenstore read failure",
      message="could not read from xenstore [path: {}]".format(path)
    )

class XenStoreDeleteError(Error):

  def __init__(self, path):
    super().__init__(
      title="xenstore delete failure",
      message="could not delete xenstore [path: {}]".format(path)
    )

class XenStore(ComMechanism):

  SOCKET_ENV = "XS_SOCKET"
  DEFAULT_SOCKET_PATH = "/var/run/xenstored/socket"

  CLICKOS_BASE_PATH = "data/clickos"
  UNIMON_BASE_PATH = "data/unimon"

  ENCODING = "utf-8"
  XS_CHUNK = 512
  MAX_TRIES = 3
  CONTROL_RESPONSE_WAIT = 1

  def __init__(self, log_level, name, message_func):
    super().__init__(log_level, name, message_func)
    self.socket_path = os.getenv(self.SOCKET_ENV, self.DEFAULT_SOCKET_PATH)
    inform(self.logger, "using xenstore socket [{}]".format(self.socket_path))

### Test Connection

  def __test_connection(self):
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        client.connect()
        return
    except:
      pass
    raise XenStoreConnectError("during initial test")

  def __is_clickos(self, dom_id):
    base_path = self.__get_base_path(dom_id)
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        if client.exists(base_path.encode(self.ENCODING)) == True:
          return
    except:
      pass
    raise NonClickOSDomError(dom_id)

  def test(self, dom_id):
    self.__test_connection() 
    self.__is_clickos(dom_id)
    success(self.logger, "connection via xenstore made")
    return True

### ----------

### Utils

  def __get_base_path(self, dom_id):
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        domain_path = client.get_domain_path(dom_id)
        if not domain_path == None:
          return "{}/{}".format(domain_path.decode(self.ENCODING), self.CLICKOS_BASE_PATH)
    except:
      pass
    raise InvalidDomainError(dom_id)

### ----------

### XenStore Usage
  # Each returns none on failure

  def __xs_write(self, dom_id, rid, data):
    base_path = self.__get_base_path(dom_id)
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        attempts = 0
        tr_id = client.transaction()
        while True:
          attempts += 1
          for p, d in data.items():
            path = "{}/{}/{}".format(base_path, str(rid), p).encode(self.ENCODING)
            client.mkdir(path)
            if len(d) != 0:
              value = d.encode(self.ENCODING)
              client.write(path, value)
          if client.commit():
            success(self.logger, "xenstore transaction [{}] complete".format(tr_id))
            return True
          if attempts >= self.MAX_TRIES:
            client.rollback()
            raise XenStoreWriteError(tr_id)
    except:
      pass
    raise XenStoreConnectError("during write")

  def __xs_read(self, dom_id, rid, path_ext):
    base_path = self.__get_base_path(dom_id)
    path = "{}/{}/{}".format(base_path, str(rid), path_ext).encode(self.ENCODING)
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        value = client.read(path)
        if value:
          return value.decode(self.ENCODING)
    except:
      pass
    raise XenStoreReadError(path.decode(self.ENCODING))

  def __xs_remove_path(self, dom_id, path_ext):
    base_path = self.__get_base_path(dom_id)
    path = "{}/{}".format(base_path, path_ext).encode(self.ENCODING)
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        client.delete(path)
        return
    except:
      pass
    raise XenStoreDeleteError(path.decode(self.ENCODING))

  def __xs_list_routers(self, dom_id):
    base_path = self.__get_base_path(dom_id)
    path = base_path.encode(self.ENCODING)
    try:
      with PyXSClient(unix_socket_path=self.socket_path) as client:
        raw_list = client.list(path)
        return raw_list
    except:
      pass
    raise XenStoreReadError(path.decode(self.ENCODING))

### ----------

### ClickOS Usage

  def __next_router_id(self, dom_id):
    base_path = self.__get_base_path(dom_id)
    raw_list = self.__xs_list_routers(dom_id)
    if len(raw_list) == 0: return -1
    routers = []
    for value in raw_list:
      value = value.decode(self.ENCODING)
      try:
        value = int(value)
        routers.append(value)
      except:
        continue
    return max(routers)

  def __router_list(self, dom_id):
    base_path = self.__get_base_path(dom_id)
    raw_list = self.__xs_list_routers(dom_id)
    routers = {}
    for value in raw_list:
      value = value.decode(self.ENCODING)
      try:
        value = int(value)
      except:
        continue
      routers[value] = self.__xs_read(dom_id, value, "status")
    return routers

  def __get_router_state(self, dom_id, rid):
    return self.__xs_read(dom_id, rid, "status")

  def __install_config(self, dom_id, config, name):
    nrid = self.__next_router_id(dom_id)
    nrid += 1
    data = {}
    data["control"] = ""
    data["elements"] = ""
    data["config_name"] = name
    data["status"] = self.ROUTER_STATUS.get("stopped")
    i = 0
    while True:
      pos = (i * self.XS_CHUNK)
      if pos >= len(config):
        break
      path_ext = "config/{}".format(i)
      chunk = config[pos:pos+self.XS_CHUNK]
      data[path_ext] = chunk
      i += 1
    self.__xs_write(dom_id, nrid, data)
    return nrid

  
  

### ----------

### Public

  def get_router_state(self, dom_id, router_id):
    return self.__get_router_state(dom_id, router_id)

  def install_click_config(self, dom_id, config, name):
    rid = self.__install_config(dom_id, config, name)
    success(self.logger, "click config installed to router [{}]".format(rid))
    return rid

  def start_router(self, dom_id, rid):
    state = self.__get_router_state(dom_id, rid)
    if state == self.ROUTER_STATUS.get("running"):
      raise StateChangeError(rid, "router already running")
    data = {"status": self.ROUTER_STATUS.get("running")}
    self.__xs_write(dom_id, rid, data)
    return rid

  def stop_router(self, dom_id, rid):
    state = self.__get_router_state(dom_id, rid)
    if state == self.ROUTER_STATUS.get("stopped"):
      raise StateChangeError(rid, "router already stopped")
    data = {"status": self.ROUTER_STATUS.get("stopped")}
    self.__xs_write(dom_id, rid, data)
    return rid

  def remove_router(self, dom_id, rid, force=False):
    state = self.__get_router_state(dom_id, rid)
    if state == self.ROUTER_STATUS.get("running"):
      if force:
        data = {"status": self.ROUTER_STATUS.get("stopped")}
        self.__xs_write(dom_id, rid, data)
      else:
        raise RouterStillRunningError(dom_id, rid)
    self.__xs_remove_path(dom_id, str(rid))
    return

  def get_router_list(self, dom_id):
    return self.__router_list(dom_id)

  def get_element_handler(self, dom_id, rid, element_name, handler_name):
    print(element_name)
    path_ext = "control/read/{}/{}".format(element_name, handler_name)
    data = {path_ext: ""}
    self.__xs_write(dom_id, rid, data)
    attempts = 0
    path_ext = "elements/{}/{}".format(element_name, handler_name)
    time.sleep(2)
    data = self.__xs_read(dom_id, rid, element_name)
    return data

### ----------
