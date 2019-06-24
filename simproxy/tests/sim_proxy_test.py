import grpc
import time

from protos import sim_proxy_pb2
from protos import sim_proxy_pb2_grpc


def main():
  data_types = {
      sim_proxy_pb2.AIRSPEED_INDICATOR_INDICATION: 'Airspeed',
      sim_proxy_pb2.HEADING_INDICATOR_INDICATION: 'Heading',
  }

  channel = grpc.insecure_channel('localhost:50051')
  stub = sim_proxy_pb2_grpc.SimProxyStub(channel)
  request = sim_proxy_pb2.WatchRequest(types=data_types.keys())
  while True:
    print 'Connecting to SimProxy...'
    try:
      responses = stub.Watch(request)
      for response in responses:
        for data in response.data:
          print '{0} = {1:.1f}'.format(data_types[data.type], data.value)
    except Exception as e:
      print e

    time.sleep(1)


if __name__ == '__main__':
  main()