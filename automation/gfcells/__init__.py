
import gdsfactory as gf
from gdsfactory.generic_tech import get_generic_pdk

gf.CONF.display_type = "klayout"

import os

if not os.getenv("GF_PDK"):
    ENV_GF_PDK = os.getenv("GF_PDK")
if not ENV_GF_PDK:
    ENV_GF_PDK = "generic"

match ENV_GF_PDK:
    case "sky130":
        pdk = None
    case "generic":
        pdk = get_generic_pdk()
pdk.activate()

from .typings import *

match ENV_GF_PDK:
    case "sky130":
        from .sky130 import *
    case "generic":
        from .routing_a import *
        from .generic_ccres import *
        from .route_solver import *
