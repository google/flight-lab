# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: client.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='client.proto',
  package='flightlab',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0c\x63lient.proto\x12\tflightlab\x1a\x1bgoogle/protobuf/empty.proto\"\x1a\n\x07Message\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1b\n\x05Image\x12\x12\n\nimage_path\x18\x02 \x01(\t\"9\n\x0fGeneralResponse\x12\x0f\n\x07succeed\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t2\xd7\x01\n\rClientService\x12\x42\n\x0e\x44isplayMessage\x12\x12.flightlab.Message\x1a\x1a.flightlab.GeneralResponse\"\x00\x12>\n\x0c\x44isplayImage\x12\x10.flightlab.Image\x1a\x1a.flightlab.GeneralResponse\"\x00\x12\x42\n\nDisplayOff\x12\x16.google.protobuf.Empty\x1a\x1a.flightlab.GeneralResponse\"\x00\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='flightlab.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='flightlab.Message.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=56,
  serialized_end=82,
)


_IMAGE = _descriptor.Descriptor(
  name='Image',
  full_name='flightlab.Image',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='image_path', full_name='flightlab.Image.image_path', index=0,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=84,
  serialized_end=111,
)


_GENERALRESPONSE = _descriptor.Descriptor(
  name='GeneralResponse',
  full_name='flightlab.GeneralResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='succeed', full_name='flightlab.GeneralResponse.succeed', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='flightlab.GeneralResponse.error_message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=113,
  serialized_end=170,
)

DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['Image'] = _IMAGE
DESCRIPTOR.message_types_by_name['GeneralResponse'] = _GENERALRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'client_pb2'
  # @@protoc_insertion_point(class_scope:flightlab.Message)
  ))
_sym_db.RegisterMessage(Message)

Image = _reflection.GeneratedProtocolMessageType('Image', (_message.Message,), dict(
  DESCRIPTOR = _IMAGE,
  __module__ = 'client_pb2'
  # @@protoc_insertion_point(class_scope:flightlab.Image)
  ))
_sym_db.RegisterMessage(Image)

GeneralResponse = _reflection.GeneratedProtocolMessageType('GeneralResponse', (_message.Message,), dict(
  DESCRIPTOR = _GENERALRESPONSE,
  __module__ = 'client_pb2'
  # @@protoc_insertion_point(class_scope:flightlab.GeneralResponse)
  ))
_sym_db.RegisterMessage(GeneralResponse)



_CLIENTSERVICE = _descriptor.ServiceDescriptor(
  name='ClientService',
  full_name='flightlab.ClientService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=173,
  serialized_end=388,
  methods=[
  _descriptor.MethodDescriptor(
    name='DisplayMessage',
    full_name='flightlab.ClientService.DisplayMessage',
    index=0,
    containing_service=None,
    input_type=_MESSAGE,
    output_type=_GENERALRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DisplayImage',
    full_name='flightlab.ClientService.DisplayImage',
    index=1,
    containing_service=None,
    input_type=_IMAGE,
    output_type=_GENERALRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DisplayOff',
    full_name='flightlab.ClientService.DisplayOff',
    index=2,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=_GENERALRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_CLIENTSERVICE)

DESCRIPTOR.services_by_name['ClientService'] = _CLIENTSERVICE

# @@protoc_insertion_point(module_scope)
