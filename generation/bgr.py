from .component import *

import subprocess
import os
from pathlib import Path

class BGR(LDOComponent):
    def __init__(self, tech: TechManager):
        super().__init__(tech)

    def generate(self):
        if "PDK_ROOT" not in os.environ:
            username = os.getenv('USER')
            pdk_root = f"/home/{username}/.volare"
            os.environ["PDK_ROOT"] = pdk_root
        proc = subprocess.Popen(
            [
                'magic',
                '-dnull',
                '-noconsole',
                "-rcfile",
                self.tech.magicrc_path(),
                "automation/thirdparty/bgr/layout/bandgaptop_hybrid_hier.mag",
		    ],
            stdin = subprocess.PIPE,
            stdout=subprocess.PIPE,
		    stderr=subprocess.STDOUT,
            cwd = ".",
            env=os.environ,
		    universal_newlines = True)
        
        path = Path('build/sky130_bgr/gds')
        path.mkdir(parents=True, exist_ok=True)
        print(proc)
        
        proc.stdin.write("gds write build/sky130_bgr/gds/bgr.gds\n")
        proc.stdin.write("quit -noprompt\n")
