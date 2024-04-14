from .component import *

import subprocess
import os
from pathlib import Path


class BGR(LDOComponent):
    def __init__(self, tech: TechManager):
        super().__init__(tech)

    def generate(self):
        if "PDK_ROOT" not in os.environ:
            username = os.getenv("USER")
            pdk_root = f"/home/{username}/.volare"
            os.environ["PDK_ROOT"] = pdk_root
        proc = subprocess.Popen(
            [
                "magic",
                "-dnull",
                "-noconsole",
                "-rcfile",
                self.tech.magicrc_path(),
                "magic/bgr-jkustin/bandgaptop_hybrid_hier.mag",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=".",
            env=os.environ,
            universal_newlines=True,
        )

        path = Path("build/sky130_bgr/gds")
        path.mkdir(parents=True, exist_ok=True)

        proc.stdin.write("gds write build/sky130_bgr/gds/bgr.gds\n")
        proc.stdin.write("quit -noprompt\n")
        proc.communicate()

        proc = subprocess.Popen(
            [
                "xschem",
                "-q",
                "-r",
                "-n",
                "--rcfile",
                "xschemrc"
                "tests/tb_bgr.sch",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd="xschem",
            env=os.environ,
            universal_newlines=True,
        )

        proc.communicate()

        # TODO: Generalize paths
        proc = subprocess.Popen(
            [
                "ngspice",
                "-b",
                "-a",
                "-o",
                "/content/pmicgen/build/sky130_bgr/bgr.report",
                "-r",
                "/content/pmicgen/build/sky130_bgr/bgr.raw",
                "-rcfile",
                "xschemrc",
                "/root/.xschem/simulations/tb_bgr.spice",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd="xschem",
            env=os.environ,
            universal_newlines=True,
        )

        proc.communicate()

