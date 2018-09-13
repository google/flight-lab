# Copyright 2018 Flight Lab authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Exposes all APIs at one place."""

import flask

from google.protobuf import json_format

from protos import controller_pb2


class ApiService(object):
  """Interface between frontend and backend.

  /system/on
    [Async] Turns on the entire system.
    Request: None
    Response: 'OK'
    Sends command to all clients to start corresponding components per config.
    A request to /config can be made to get individual component status.

  /system/off
    [Async] Turns off the entire system.
    Request: None
    Response: 'OK'
    Sends command to all clients to stop corresponding components per config.
    A request to /config can be made to get individual component status.

  /system/restart
    [Async] Restarts all software on all machines.
    Request: None
    Response: 'OK'
    Sends command to all clients to restart software components only.
    A request to /config can be made to get individual component status.

  /config
    Get system configuration and latest component status.
    Request: None
    Response: flightlab.System protobuf in json format.
    This api can be used for UI to show components dynamically based on
    latest configuration. Latest status of individual components are also
    available for display.

  /state
    Get current intended system state.
    Request: None
    Response: flightlab.System.ON or flightlab.System.OFF.
    Uses this api to retrieve currently selected system state (on or off). It
    does reflect the actual state of the system as each component is turned on
    or off asynchronously and may be in different progress.

  /exit
    Terminates all clients.
    Request: None
    Response: 'OK'
  """

  def __init__(self, web, system_config, control_service):
    """Initializes API service.

    Args:
      web: Flask instance.
      system_config: the system config protobuf.
      control_service: service to control clients.
    """
    self._system_config = system_config
    self._control_service = control_service
    web.add_url_rule('/system/on', view_func=self._system_on)
    web.add_url_rule('/system/off', view_func=self._system_off)
    web.add_url_rule('/system/restart', view_func=self._system_restart)
    web.add_url_rule('/config', view_func=self._config)
    web.add_url_rule('/state', view_func=self._state)
    web.add_url_rule('/exit', view_func=self._exit)
    web.add_url_rule('/debug', view_func=self._debug)

  def _system_on(self):
    self._control_service.send_command(controller_pb2.SystemCommand.START)
    return 'OK'

  def _system_off(self):
    self._control_service.send_command(controller_pb2.SystemCommand.STOP)
    return 'OK'

  def _system_restart(self):
    self._control_service.send_command(controller_pb2.SystemCommand.RESTART)
    return 'OK'

  def _config(self):
    return self._respond_json(self._system_config)

  def _state(self):
    state = controller_pb2.SystemState(state=self._system_config.state)
    return self._respond_json(state)

  def _exit(self):
    self._control_service.send_command(controller_pb2.SystemCommand.EXIT)
    return 'OK'

  def _debug(self):
    self._control_service.send_command(controller_pb2.SystemCommand.DEBUG)
    return 'OK'

  def _respond_json(self, msg):
    content = json_format.MessageToJson(msg)
    return flask.Response(
        response=content, status=200, mimetype='application/json')
