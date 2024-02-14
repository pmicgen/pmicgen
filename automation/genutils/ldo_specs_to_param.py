import yaml
from .component import LDOComponent

# TODO: Change base class
class LDOSpecToParam(LDOComponent):
    def __init__(spec_0, spec_1, spec_2):
        self.spec_0 = spec_0
        self.spec_1 = spec_1
        self.spec_2 = spec_2
    
    def generate():
        specs = {
            "ota": {
                "netlist": "netlist/path/file.spice",
            }
            "pmosw": {
                "mult": "40",
            }
            "ccr": {
                "ratio": "0.5",
                "m": "5",
                "n": "5",
            }
        }
        
        with open('data.yml', 'w') as outfile:
            yaml.dump(specs, outfile, default_flow_style=False)
        