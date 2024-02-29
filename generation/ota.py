from .component import *

from align import schematic2layout
import os


class OTA(LDOComponent):

    schematic_path: os.PathLike

    def __init__(self, tech: TechManager, netlist: os.PathLike):
        super().__init__(tech)
        self.netlist = netlist

    def generate(self):
        """
        client = docker.from_env()
        path = Path(self.netlist).as_posix()
        container = client.containers.run(
            "darpaalign/align-public:latest",
            command=f"schematic2layout.py /pdk/sky130/examples/telescopic_ota -p /pdk/sky130/SKY130_PDK",
            volumes={os.path.abspath("automation/thirdparty/align-sky130"): {'bind': '/pdk/sky130', 'mode': 'rw'}},
        )
        stream, _ = container.get_archive("work/TELESCOPIC_OTA_0.gds")

        # Destination path outside the container
        destination_path = os.path.join(os.getcwd(), "TELESCOPIC_OTA_0.gds")
        
        # Extract the artifact from the stream and save it
        with open(destination_path, "wb") as f_out:
            shutil.copyfileobj(stream, f_out)
        
        # Remove the container
        container.remove()
        """
        schematic2layout()
        
