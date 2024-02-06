from .component import *

import subprocess
import os


class BGR(LDOComponent):
    def __init__(self, tech: TechManager):
        super().__init__(tech)

    def generate(self):
        proc = subprocess.run(
            [
                "magic",
                "-dnull",
                "-noconsole",
                f"-rcfile {self.tech.magicrc_path()}",
                f"automation/thirdparty/bgr/layout/bandgaptop_hybrid_hier.mag",
            ],
            cwd=".",
            env=os.environ.copy(),
            input="gds write bgr",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

