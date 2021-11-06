from setuptools import setup, find_packages

# pip install rma
# rma -s redis_cache -x -


setup(
   name="redis_helper",
   version="0.1.0",
   description="A helper for Redis operations used for NQN",
   author='Blue',
   url="https://nqn.blue/",
   packages=find_packages(),
   install_requires=["msgpack", "async_generator", "protobuf"]
)
