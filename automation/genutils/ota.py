from .component import *

import docker
import os


class OTA(LDOComponent):

    schematic_path: os.PathLike

    def __init__(self, tech: TechManager, netlist: os.PathLike):
        super().__init__(tech)
        self.netlist = netlist

    def generate(self):
        client = docker.from_env()
        container = client.containers.run(
            "darpaalign/align-public:latest",
            volumes={"automation/thirdparty/align-sky130": "/pdk/sky130"},
        )
        container.exec_run(
            f"schematic2layout.py {self.schematic_path.as_posix()} -p /pdk/sky130"
        )
        #container.get_archive()
