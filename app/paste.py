(asr_env) PS C:\Users\re_nikitav\utils-poc\asr_nvidia_parakeet_realtime> pip install -r .\requirements.txt
Collecting fastapi==0.110.0 (from -r .\requirements.txt (line 1))
  Using cached fastapi-0.110.0-py3-none-any.whl.metadata (25 kB)
Collecting nemo_toolkit>=2.5.0 (from nemo_toolkit[asr]>=2.5.0->-r .\requirements.txt (line 2))
  Using cached nemo_toolkit-2.5.3-py3-none-any.whl.metadata (95 kB)
Collecting numpy (from -r .\requirements.txt (line 3))
  Using cached numpy-2.3.5-cp313-cp313-win_amd64.whl.metadata (60 kB)
Collecting psutil==5.9.8 (from -r .\requirements.txt (line 4))
  Downloading psutil-5.9.8-cp37-abi3-win_amd64.whl.metadata (22 kB)
Collecting pydantic==2.6.3 (from -r .\requirements.txt (line 5))
  Downloading pydantic-2.6.3-py3-none-any.whl.metadata (84 kB)
Collecting sounddevice==0.4.6 (from -r .\requirements.txt (line 6))
  Downloading sounddevice-0.4.6-py3-none-win_amd64.whl.metadata (1.4 kB)
Collecting soundfile==0.12.1 (from -r .\requirements.txt (line 7))
  Downloading soundfile-0.12.1-py2.py3-none-win_amd64.whl.metadata (14 kB)
Collecting uvicorn==0.29.0 (from -r .\requirements.txt (line 8))
  Downloading uvicorn-0.29.0-py3-none-any.whl.metadata (6.3 kB)
Collecting websockets==12.0 (from -r .\requirements.txt (line 9))
  Downloading websockets-12.0-py3-none-any.whl.metadata (6.6 kB)
Collecting starlette<0.37.0,>=0.36.3 (from fastapi==0.110.0->-r .\requirements.txt (line 1))
  Downloading starlette-0.36.3-py3-none-any.whl.metadata (5.9 kB)
Requirement already satisfied: typing-extensions>=4.8.0 in c:\users\re_nikitav\utils-poc\asr_nvidia_parakeet_realtime\asr_env\lib\site-packages (from fastapi==0.110.0->-r .\requirements.txt (line 1)) (4.15.0)
Collecting annotated-types>=0.4.0 (from pydantic==2.6.3->-r .\requirements.txt (line 5))
  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.16.3 (from pydantic==2.6.3->-r .\requirements.txt (line 5))
  Downloading pydantic_core-2.16.3.tar.gz (368 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Installing backend dependencies ... done
  Preparing metadata (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [75 lines of output]
      Python reports SOABI: cp313-win_amd64
      Computed rustc target triple: x86_64-pc-windows-msvc
      Installation directory: C:\Users\re_nikitav\AppData\Local\puccinialin\puccinialin\Cache
      Downloading rustup-init from https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
      Checking for Rust toolchain....
      Rust not found, installing into a temporary directory

      Downloading rustup-init:   0%|          | 0.00/13.6M [00:00<?, ?B/s]
      Downloading rustup-init:   1%|1         | 139k/13.6M [00:00<00:09, 1.38MB/s]
      Downloading rustup-init:   2%|2         | 279k/13.6M [00:00<00:12, 1.10MB/s]
      Downloading rustup-init:   3%|2         | 393k/13.6M [00:00<00:15, 831kB/s]
      Downloading rustup-init:   4%|3         | 500k/13.6M [00:00<00:30, 423kB/s]
      Downloading rustup-init:   5%|4         | 614k/13.6M [00:01<00:23, 542kB/s]
      Downloading rustup-init:   6%|5         | 745k/13.6M [00:01<00:18, 687kB/s]
      Downloading rustup-init:   7%|6         | 893k/13.6M [00:01<00:15, 812kB/s]
      Downloading rustup-init:   8%|7         | 1.07M/13.6M [00:01<00:12, 1.03MB/s]
      Downloading rustup-init:   9%|9         | 1.24M/13.6M [00:01<00:11, 1.04MB/s]
      Downloading rustup-init:  11%|#         | 1.43M/13.6M [00:01<00:10, 1.15MB/s]
      Downloading rustup-init:  12%|#1        | 1.59M/13.6M [00:01<00:09, 1.26MB/s]
      Downloading rustup-init:  13%|#3        | 1.80M/13.6M [00:01<00:08, 1.47MB/s]
      Downloading rustup-init:  15%|#4        | 2.00M/13.6M [00:01<00:07, 1.60MB/s]
      Downloading rustup-init:  16%|#6        | 2.17M/13.6M [00:02<00:08, 1.41MB/s]
      Downloading rustup-init:  18%|#7        | 2.41M/13.6M [00:02<00:06, 1.64MB/s]
      Downloading rustup-init:  20%|#9        | 2.65M/13.6M [00:02<00:05, 1.84MB/s]
      Downloading rustup-init:  22%|##1       | 2.92M/13.6M [00:02<00:05, 2.06MB/s]
      Downloading rustup-init:  23%|##3       | 3.14M/13.6M [00:02<00:05, 1.86MB/s]
      Downloading rustup-init:  25%|##4       | 3.33M/13.6M [00:02<00:07, 1.34MB/s]
      Downloading rustup-init:  26%|##6       | 3.54M/13.6M [00:02<00:06, 1.49MB/s]
      Downloading rustup-init:  29%|##8       | 3.89M/13.6M [00:03<00:04, 1.95MB/s]
      Downloading rustup-init:  31%|###1      | 4.26M/13.6M [00:03<00:03, 2.34MB/s]
      Downloading rustup-init:  33%|###3      | 4.52M/13.6M [00:03<00:03, 2.41MB/s]
      Downloading rustup-init:  35%|###5      | 4.80M/13.6M [00:03<00:03, 2.49MB/s]
      Downloading rustup-init:  38%|###7      | 5.10M/13.6M [00:03<00:03, 2.48MB/s]
      Downloading rustup-init:  40%|####      | 5.47M/13.6M [00:03<00:03, 2.61MB/s]
      Downloading rustup-init:  42%|####2     | 5.74M/13.6M [00:03<00:04, 1.62MB/s]
      Downloading rustup-init:  45%|####4     | 6.09M/13.6M [00:04<00:03, 1.96MB/s]
      Downloading rustup-init:  47%|####7     | 6.41M/13.6M [00:04<00:03, 2.20MB/s]
      Downloading rustup-init:  50%|#####     | 6.78M/13.6M [00:04<00:02, 2.54MB/s]
      Downloading rustup-init:  54%|#####3    | 7.29M/13.6M [00:04<00:02, 2.36MB/s]
      Downloading rustup-init:  56%|#####6    | 7.62M/13.6M [00:04<00:02, 2.21MB/s]
      Downloading rustup-init:  58%|#####8    | 7.87M/13.6M [00:04<00:02, 2.26MB/s]
      Downloading rustup-init:  61%|######    | 8.23M/13.6M [00:04<00:02, 2.56MB/s]
      Downloading rustup-init:  64%|######4   | 8.70M/13.6M [00:04<00:01, 3.07MB/s]
      Downloading rustup-init:  67%|######6   | 9.08M/13.6M [00:05<00:01, 3.20MB/s]
      Downloading rustup-init:  70%|######9   | 9.42M/13.6M [00:05<00:01, 2.62MB/s]
      Downloading rustup-init:  72%|#######2  | 9.82M/13.6M [00:05<00:01, 2.94MB/s]
      Downloading rustup-init:  75%|#######4  | 10.1M/13.6M [00:05<00:01, 2.95MB/s]
      Downloading rustup-init:  78%|#######8  | 10.6M/13.6M [00:05<00:00, 3.31MB/s]
      Downloading rustup-init:  81%|########  | 10.9M/13.6M [00:05<00:00, 3.22MB/s]
      Downloading rustup-init:  83%|########3 | 11.3M/13.6M [00:06<00:01, 1.21MB/s]
      Downloading rustup-init:  89%|########9 | 12.1M/13.6M [00:06<00:00, 2.05MB/s]
      Downloading rustup-init:  92%|#########2| 12.5M/13.6M [00:06<00:00, 2.28MB/s]
      Downloading rustup-init:  95%|#########5| 12.9M/13.6M [00:06<00:00, 2.54MB/s]
      Downloading rustup-init:  98%|#########7| 13.3M/13.6M [00:06<00:00, 2.78MB/s]
      Downloading rustup-init: 100%|##########| 13.6M/13.6M [00:07<00:00, 1.93MB/s]
      Installing rust to C:\Users\re_nikitav\AppData\Local\puccinialin\puccinialin\Cache\rustup
      warn: installing msvc toolchain without its prerequisites
      info: profile set to 'minimal'
      info: default host triple is x86_64-pc-windows-msvc
      info: syncing channel updates for 'stable-x86_64-pc-windows-msvc'
      info: latest update on 2025-11-10, rust version 1.91.1 (ed61e7d7e 2025-11-07)
      info: downloading component 'cargo'
      info: downloading component 'rust-std'
      info: downloading component 'rustc'
      info: installing component 'cargo'
      info: installing component 'rust-std'
      info: installing component 'rustc'
      info: default toolchain set to 'stable-x86_64-pc-windows-msvc'
      Checking if cargo is installed
      cargo 1.91.1 (ea2d97820 2025-10-10)

      Cargo, the Rust package manager, is not installed or is not on PATH.
      This package requires Rust and Cargo to compile extensions. Install it through
      the system's package manager or via https://rustup.rs/

      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.

[notice] A new release of pip is available: 24.3.1 -> 25.3
[notice] To update, run: python.exe -m pip install --upgrade pip
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
(asr_env) PS C:\Users\re_nikitav\utils-poc\asr_nvidia_parakeet_realtime> 
