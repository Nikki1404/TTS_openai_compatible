https://huggingface.co/nvidia/parakeet_realtime_eou_120m-v1


==========
== CUDA ==
==========

CUDA Version 12.1.1

Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.

Traceback (most recent call last):
  File "/app/ws_kokoro_server.py", line 31, in <module>
    CONFIG = yaml.safe_load(f)
  File "/usr/local/lib/python3.10/dist-packages/yaml/__init__.py", line 125, in safe_load
    return load(stream, SafeLoader)
  File "/usr/local/lib/python3.10/dist-packages/yaml/__init__.py", line 81, in load
    return loader.get_single_data()
  File "/usr/local/lib/python3.10/dist-packages/yaml/constructor.py", line 49, in get_single_data
    node = self.get_single_node()
  File "/usr/local/lib/python3.10/dist-packages/yaml/composer.py", line 39, in get_single_node
    if not self.check_event(StreamEndEvent):
  File "/usr/local/lib/python3.10/dist-packages/yaml/parser.py", line 98, in check_event
    self.current_event = self.state()
  File "/usr/local/lib/python3.10/dist-packages/yaml/parser.py", line 171, in parse_document_start
    raise ParserError(None, None,
yaml.parser.ParserError: expected '<document start>', but found '<block mapping start>'
  in "config.yaml", line 4, column 1
 
