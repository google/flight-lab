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
"""Library for common patterns."""

import logging
import sys
import threading
import time
import traceback


class Startable(object):
  """Interface for any class that should be started at the beginning."""

  def start(self):
    raise NotImplementedError()


class Stopable(object):
  """Interface for any class that should be stopped at the end."""

  def stop(self):
    raise NotImplementedError()


class Closable(object):
  """Interface for any class that should be closed at the end."""

  def close(self):
    raise NotImplementedError()


class Logger(object):
  """For any class that needs to produce log.

  Class name will be used as logger name.

  Usage:
    self.logger.info(msg)
    self.logger.warning(msg)
    self.logger.error(msg)
    self.logger.debug(msg)
  """

  def __init__(self, *args, **kwargs):
    super(Logger, self).__init__(*args, **kwargs)
    self._logger = logging.getLogger(self.__class__.__name__)

  @property
  def logger(self):
    return self._logger


class EventEmitter(Closable):
  """For any class that needs to emit events.

  To emit an event:
    self.emit('name of event', event-dependent arguments)
  To subscribe an event:
    x = MyClass()  # which is derived from EventEmitter
    ...
    x.on('[name of event]', my_handler)

    def my_handler(event-dependent arguments):
      ...
  """

  def __init__(self, *args, **kwargs):
    super(EventEmitter, self).__init__()
    self._event_handlers = {}

  def on(self, event, callback):
    """Subscribes an event.

    Args:
      event: name of the event to subscribe.
      callback: function to callback when the event is triggered.
    Returns:
      self.
    """
    assert self._event_handlers is not None

    if event not in self._event_handlers:
      self._event_handlers[event] = []
    self._event_handlers[event].append(callback)
    return self

  def off(self, event, callback):
    """Unsubscribes an event.

    Args:
      event: name of the event to unsubscribe.
      callback: callback function to unsubscribe.
    Returns:
      Self.
    """
    assert self._event_handlers is not None
    if event in self._event_handlers:
      del self._event_handlers[event]
    return self

  def emit(self, event, *args, **kwargs):
    """Emits an event.

    Args:
      event: name of the event. It can be arbitrary string, but should be well
             documented with its arguments in class documentation.
      *args: unnamed arguments of the event.
      **kwargs: named arguments of the event.
    Returns:
      Self.
    """
    assert self._event_handlers is not None

    if event in self._event_handlers:
      for handler in self._event_handlers[event]:
        handler(*args, **kwargs)

    return self

  def close(self):
    self._event_handlers = None
    super(EventEmitter, self).close()


class Worker(Startable, Stopable, Closable, Logger):
  """Base class to support background thread.

  Subclasses only need to implement the following methods:
    _on_start() (optional)
    _on_run()
    _on_stop()  (optional)

  If sleeping is needed, subclass shall call self._sleep() instead of
  time.sleep() to ensure stop() can immediately break the sleep.

  Execution flow:
    Caller thread         Background thread
      start()
                            _on_start()
                            _on_run()  (called repeatedly)
      stop()
                            _on_stop()
  """

  def __init__(self, worker_name=None, *args, **kwargs):
    """Initialize a worker class.

    Args:
      worker_name: name for the background thread. This helps to identify
                  threads when debugging. If not set, class name will be used.
    """
    super(Worker, self).__init__(*args, **kwargs)
    self._worker_name = worker_name if worker_name else self.__class__.__name__
    self._worker_thread = None
    self._abort_event = threading.Event()

  def start(self):
    """Starts the background thread."""
    if self._worker_thread and self._worker_thread.is_alive():
      return

    self._abort_event.clear()
    self._worker_thread = threading.Thread(
        name=self._worker_name, target=self._run)
    self._worker_thread.daemon = True
    self._worker_thread.start()

  def stop(self):
    """Stops the background thread.

    The call will be blocked until background thread exits.
    """
    if not self._worker_thread:
      return

    if not self._worker_thread.is_alive():
      self._worker_thread = None
      return

    self._abort_event.set()
    self._worker_thread.join()
    self._worker_thread = None

  def close(self):
    self.stop()
    super(Worker, self).close()

  def _run(self):
    """Runs as background thread and stops when stop() is called."""
    if self._on_start() is False:
      self._on_stop()
      return

    while not self._abort_event.is_set():
      try:
        if self._on_run() is False:
          break
      except Exception as e:
        try:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
          self.logger.warn('\n'.join(msg))
        except:
          self.logger.warn('Exception: {0}'.format(e))

    self._on_stop()

  def _on_start(self):
    """Overrides this method to perform initialization work before loop.

    Returns:
      False to abort background thread.
    """
    pass

  def _on_run(self):
    """Overrides this method to perform tasks.

    This method will be called repeatedly. Any raised exception will be logged
    and will NOT cause background thread to abort.

    Returns:
      False to exit background thread.
    """
    self._sleep(1)

  def _on_stop(self):
    """Overrides this method to perform cleanup work before exit."""
    pass

  def _sleep(self, seconds):
    """Suspends execution of background thread for the given number of seconds.

    This method should be used instead of time.sleep() to ensure when stop() is
    called, sleep can wake up immediately and exit background thread.

    Args:
      seconds: time to sleep in seconds.
    """
    self._abort_event.wait(seconds)


def run_as_thread(name, target, args=(), kwargs={}):
  """Run a function as separate thread.

  This helper function ensures:
    * the thread won't block Python program from exiting
    * log exceptions using Python logging.

  Args:
    target: function to run in separate thread.
    args: a tuple of all unnamed arguments.
    kwargs: a dictionary of all named arguments.
  Returns:
    Thread instance.
  """
  kwargs['thread_target'] = target
  t = threading.Thread(
      name=name, target=_thread_wrapper, args=args, kwargs=kwargs)
  t.daemon = True
  t.start()
  return t


def _thread_wrapper(thread_target, *args, **kwargs):
  """Runs the target function and log any raised exception."""
  logger = logging.getLogger(threading.current_thread().name)
  try:
    thread_target(*args, **kwargs)
  except Exception as e:
    try:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
      logger.error('\n'.join(msg))
    except:
      logger.error('Exception: {0}'.format(e))
