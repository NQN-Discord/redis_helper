# WSL:
#  protoc -I=. --rust_out=../../../StateKeeperRust/src/protobuf/ --python_out=. ./discord.proto

# Where "\t\x14p\x02\xbdZ\x8bL\r\x19P0\x82|:t\xf4\x0c\"\bcommands(\x0b" is the result from a redis get:
# python3 -c 'print(bytearray(b"\t\x14p\x02\xbdZ\x8bL\r\x19P0\x82|:t\xf4\x0c\"\bcommands(\x0b").hex())' | xxd -r -p | protoc --decode MeMemberData /mnt/f/Python/NQN/redis_helper/redis_helper/protobuf/discord.proto --proto_path /