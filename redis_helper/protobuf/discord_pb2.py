# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: discord.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rdiscord.proto\"\x91\x01\n\x08RoleData\x12\n\n\x02id\x18\x01 \x01(\x06\x12\x10\n\x08position\x18\x02 \x01(\x05\x12\x13\n\x0bpermissions\x18\x03 \x01(\x04\x12\x13\n\x0bmentionable\x18\x04 \x01(\x08\x12\x0f\n\x07managed\x18\x05 \x01(\x08\x12\x13\n\x06\x62ot_id\x18\x06 \x01(\x06H\x00\x88\x01\x01\x12\x0c\n\x04name\x18\x07 \x01(\tB\t\n\x07_bot_id\"{\n\tEmojiData\x12\n\n\x02id\x18\x01 \x01(\x06\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08\x61nimated\x18\x03 \x01(\x08\x12\x14\n\x07managed\x18\x04 \x01(\x08H\x00\x88\x01\x01\x12\x11\n\tavailable\x18\x05 \x01(\x08\x12\r\n\x05roles\x18\x06 \x03(\x06\x42\n\n\x08_managed\"\xce\x03\n\x0b\x43hannelData\x12\n\n\x02id\x18\x01 \x01(\x06\x12\x15\n\x08guild_id\x18\x02 \x01(\x06H\x00\x88\x01\x01\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x1a\n\x04type\x18\x04 \x01(\x0e\x32\x0c.ChannelType\x12\x0c\n\x04nsfw\x18\x05 \x01(\x08\x12\x10\n\x08position\x18\x06 \x01(\x05\x12\x1b\n\x13rate_limit_per_user\x18\x07 \x01(\r\x12J\n\x15permission_overwrites\x18\x08 \x03(\x0b\x32+.ChannelData.ChannelPermissionOverwriteData\x1a\xdb\x01\n\x1e\x43hannelPermissionOverwriteData\x12\n\n\x02id\x18\x01 \x01(\x06\x12X\n\x04type\x18\x02 \x01(\x0e\x32J.ChannelData.ChannelPermissionOverwriteData.ChannelPermissionOverwriteType\x12\r\n\x05\x61llow\x18\x03 \x01(\x04\x12\x0c\n\x04\x64\x65ny\x18\x04 \x01(\x04\"6\n\x1e\x43hannelPermissionOverwriteType\x12\x08\n\x04ROLE\x10\x00\x12\n\n\x06MEMBER\x10\x01\x42\x0b\n\t_guild_id\"U\n\nThreadData\x12\n\n\x02id\x18\x01 \x01(\x06\x12\x11\n\tparent_id\x18\x02 \x01(\x06\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x1a\n\x04type\x18\x04 \x01(\x0e\x32\x0c.ChannelType\"\x85\x01\n\x0cMeMemberData\x12\r\n\x05roles\x18\x01 \x03(\x06\x12\x11\n\x04nick\x18\x02 \x01(\tH\x00\x88\x01\x01\x12)\n\x1c\x63ommunication_disabled_until\x18\x03 \x01(\x03H\x01\x88\x01\x01\x42\x07\n\x05_nickB\x1f\n\x1d_communication_disabled_until*\x81\x02\n\x0b\x43hannelType\x12\x0e\n\nGUILD_TEXT\x10\x00\x12\x06\n\x02\x44M\x10\x01\x12\x0f\n\x0bGUILD_VOICE\x10\x02\x12\x0c\n\x08GROUP_DM\x10\x03\x12\x12\n\x0eGUILD_CATEGORY\x10\x04\x12\x0e\n\nGUILD_NEWS\x10\x05\x12\x0f\n\x0bGUILD_STORE\x10\x06\x12\x11\n\rPUBLIC_THREAD\x10\x07\x12\x12\n\x0ePRIVATE_THREAD\x10\x08\x12\x15\n\x11GUILD_STAGE_VOICE\x10\t\x12\x15\n\x11GUILD_NEWS_THREAD\x10\n\x12\x17\n\x13GUILD_PUBLIC_THREAD\x10\x0b\x12\x18\n\x14GUILD_PRIVATE_THREAD\x10\x0c\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'discord_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CHANNELTYPE._serialized_start=979
  _CHANNELTYPE._serialized_end=1236
  _ROLEDATA._serialized_start=18
  _ROLEDATA._serialized_end=163
  _EMOJIDATA._serialized_start=165
  _EMOJIDATA._serialized_end=288
  _CHANNELDATA._serialized_start=291
  _CHANNELDATA._serialized_end=753
  _CHANNELDATA_CHANNELPERMISSIONOVERWRITEDATA._serialized_start=521
  _CHANNELDATA_CHANNELPERMISSIONOVERWRITEDATA._serialized_end=740
  _CHANNELDATA_CHANNELPERMISSIONOVERWRITEDATA_CHANNELPERMISSIONOVERWRITETYPE._serialized_start=686
  _CHANNELDATA_CHANNELPERMISSIONOVERWRITEDATA_CHANNELPERMISSIONOVERWRITETYPE._serialized_end=740
  _THREADDATA._serialized_start=755
  _THREADDATA._serialized_end=840
  _MEMEMBERDATA._serialized_start=843
  _MEMEMBERDATA._serialized_end=976
# @@protoc_insertion_point(module_scope)
