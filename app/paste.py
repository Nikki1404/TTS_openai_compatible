(asr_env) PS C:\Users\re_nikitav\utils-poc\asr_nvidia_parakeet_realtime> pip install -r .\requirements.txt
Collecting fastapi==0.110.0 (from -r .\requirements.txt (line 1))
  Using cached fastapi-0.110.0-py3-none-any.whl.metadata (25 kB)
Collecting nemo_toolkit>=2.5.0 (from nemo_toolkit[asr]>=2.5.0->-r .\requirements.txt (line 2))
  Using cached nemo_toolkit-2.5.3-py3-none-any.whl.metadata (95 kB)
Collecting numpy==1.26.4 (from -r .\requirements.txt (line 3))
  Using cached numpy-1.26.4.tar.gz (15.8 MB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Installing backend dependencies ... done
  Preparing metadata (pyproject.toml) ... error
  error: subprocess-exited-with-error
  
  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [21 lines of output]
      + C:\Users\re_nikitav\utils-poc\asr_nvidia_parakeet_realtime\asr_env\Scripts\python.exe C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e\vendored-meson\meson\meson.py setup C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e\.mesonpy-5za04vr_ -Dbuildtype=release -Db_ndebug=if-release -Db_vscrt=md --native-file=C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e\.mesonpy-5za04vr_\meson-python-native-file.ini
      The Meson build system
      Version: 1.2.99
      Source dir: C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e
      Build dir: C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e\.mesonpy-5za04vr_
      Build type: native build
      Project name: NumPy
      Project version: 1.26.4
      WARNING: Failed to activate VS environment: Could not find C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe

      ..\meson.build:1:0: ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang'], ['clang-cl'], ['pgcc']]
      The following exception(s) were encountered:
      Running `icl ""` gave "[WinError 2] The system cannot find the file specified"
      Running `cl /?` gave "[WinError 2] The system cannot find the file specified"
      Running `cc --version` gave "[WinError 2] The system cannot find the file specified"
      Running `gcc --version` gave "[WinError 2] The system cannot find the file specified"
      Running `clang --version` gave "[WinError 2] The system cannot find the file specified"
      Running `clang-cl /?` gave "[WinError 2] The system cannot find the file specified"
      Running `pgcc --version` gave "[WinError 2] The system cannot find the file specified"

      A full log can be found at C:\Users\re_nikitav\AppData\Local\Temp\1\pip-install-mc0el2nv\numpy_ccedd31933954cb19e1753bf60baca3e\.mesonpy-5za04vr_\meson-logs\meson-log.txt
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.

[notice] A new release of pip is available: 24.3.1 -> 25.3
[notice] To update, run: python.exe -m pip install --upgrade pip
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
