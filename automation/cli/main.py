from component import *
from ota import OTA
from ccres import CCResistor

import argparse

def main():
    parser = argparse.ArgumentParser(
                    prog='LDO CAC',
                    description='Automated generation of an LDO for SKY130',
                    epilog='AC3E 2024')
    parser.add_argument('component', type=LDOComponentType, choices=list(LDOComponentType))
    args = parser.parse_args()

    match str(args.component):
        case LDOComponentType.PASS_TRANSISTOR.value:
            component = PassTransistor()
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
