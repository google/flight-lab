import socket


def get_ip():
  """Get primary IP (the one with a default route) of local machine.

  This works on both Linux and Windows platforms, and doesn't require working
  internet connection.
  """

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    # doesn't even have to be reachable
    s.connect(('10.255.255.255', 1))
    return s.getsockname()[0]
  except:
    return '127.0.0.1'
  finally:
    s.close()
