import sys
import os
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))
from genutils import *

import argparse

def main():
    parser = argparse.ArgumentParser(
                    prog='LDO CAC',
                    description='Automated generation of an LDO for SKY130',
                    epilog='AC3E 2024')
    parser.add_argument('pdk', type=PDK, choices=list(PDK))
    subparsers = parser.add_subparsers(dest="component")
    
    parser_passtrans = subparsers.add_parser(LDOComponentType.PASS_TRANSISTOR.value)
    parser_passtrans.add_argument("pcell")
    parser_passtrans = subparsers.add_parser(LDOComponentType.OTA.value)
    parser_passtrans = subparsers.add_parser(LDOComponentType.CCRESISTOR.value)
    parser_passtrans = subparsers.add_parser(LDOComponentType.BANDGAP.value)

    args = parser.parse_args()
    print(args)

    tech = TechManager(args.pdk)
    match str(args.component):
        case LDOComponentType.PASS_TRANSISTOR.value:
            component = PassTransistor(tech=tech, p_cell=int(args.pcell))
            component.generate()
        case LDOComponentType.OTA.value:
            component = OTA()
            component.generate()
        case LDOComponentType.CCRESISTOR.value:
            component = CCResistor()
            component.generate()
        case LDOComponentType.BANDGAP.value:
            component = Bandgap()
            component.generate()
        case LDOComponentType.LDO.value:
            component = LDO()
            component.generate()
        case _:
            raise argparse.ArgumentTypeError(f"Invalid component: {args.component}")

if __name__ == "__main__":
    main()
