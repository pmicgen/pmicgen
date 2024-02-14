import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from genutils import *

import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="pmicgen",
        description="Automated generation of an PMIC for SKY130",
        epilog="AC3E 2024",
    )
    parser.add_argument("--tech", type=PDK, choices=list(PDK))
    subparsers = parser.add_subparsers(dest="component")

    parser_pmosw = subparsers.add_parser(LDOComponentType.PMOS_WAFFLE.value)
    parser_pmosw.add_argument("mult")

    parser_ota = subparsers.add_parser(LDOComponentType.OTA.value)
    parser_ota.add_argument("--netlist")

    parser_ccr = subparsers.add_parser(LDOComponentType.CCRESISTOR.value)
    parser_ccr.add_argument("--columns", "-m")
    parser_ccr.add_argument("--rows", "-n")
    parser_ccr.add_argument("rwidth")
    parser_ccr.add_argument("rlength")

    subparsers.add_parser(LDOComponentType.BGR.value)

    args = parser.parse_args()
    tech = TechManager(args.tech)
    match str(args.component):
        case LDOComponentType.PMOS_WAFFLE.value:
            component = PMOSWaffle(tech=tech, mult=int(args.mult))
            component.generate()
        case LDOComponentType.OTA.value:
            component = OTA(tech=tech, netlist=str(args.netlist)
            component.generate()
        case LDOComponentType.CCRESISTOR.value:
            component = CCResistor(tech=tech, columns=int(columns), rows=int(rows))
            component.generate()
        case LDOComponentType.BGR.value:
            component = BGR(tech=tech)
            component.generate()
        case LDOComponentType.LDO.value:
            component = LDO(tech=tech)
            component.generate()
        case "ldo_specs":
            pass
        case "pmic_specs":
            pass
        case _:
            raise argparse.ArgumentTypeError(f"Invalid component: {args.component}")


if __name__ == "__main__":
    main()
