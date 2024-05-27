from pathlib import Path
import os
home = str(Path.home())

settings ={
    'data_root': f"{home}/SynologyDrive/.EscapePlan",
    "gate": [-500000, -20, 0, 10, 12, 14, 17, 21, 27, 43, 300000]
}

def set_env():
    os.environ['PATH'] = f"{os.environ['PATH']}:/usr/local/cuda-12.2/bin"
    os.environ['CUDNN_PATH'] = f"{home}/.local/lib/python3.12/site-packages/nvidia/cudnn"
    os.environ['LD_LIBRARY_PATH'] = f"{os.environ['CUDNN_PATH']}/lib:/usr/local/cuda-12.2/lib64"

