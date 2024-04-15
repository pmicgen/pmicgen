from .component import *
from pathlib import Path
import subprocess
import sys
import os


class PMOSWaffle(LDOComponent):
    p_cell: int

    def __init__(self, tech: TechManager, mult: int) -> None:
        super().__init__(tech)
        p_cells = {4512: 48, 1300: 32, 480: 28}
        p_cell = p_cells[mult]
        self.p_cell = p_cell
        self.mult = mult

    def _waffle_folder() -> str:
        #return f"{pathlib.Path(__file__).parent.parent.resolve()}/magic/moswaffle"
        return "/content/pmicgen/magic/moswaffle"

    def _update_tcl_file(self) -> None:
        pmos_tcl = open(f"{PMOSWaffle._waffle_folder()}/waffles_pmos.tcl", "r")
        pmos_data = []

        for line in pmos_tcl:
            pmos_data.append(line)
        pmos_tcl.close()

        pmos_data[12] = "set n " + str(self.p_cell) + "\n"
        pmos_data[30] = (
            f"save {PMOSWaffle._waffle_folder()}/pmos_waffle_"
            + str(self.p_cell)
            + "x"
            + str(self.p_cell)
            + "\n"
        )
        pmos_data[31] = (
            f"load {PMOSWaffle._waffle_folder()}/pmos_waffle_"
            + str(self.p_cell)
            + "x"
            + str(self.p_cell)
            + "\n"
        )
        pmos_data[-12] = (
            f"save {PMOSWaffle._waffle_folder()}/pmos_flat_"
            + str(self.p_cell)
            + "x"
            + str(self.p_cell)
            + "\n"
        )
        pmos_data[-21] = (
            "load pmos_flat_" + str(self.p_cell) + "x" + str(self.p_cell) + "\n"
        )
        pmos_data[-22] = (
            "flatten pmos_flat_" + str(self.p_cell) + "x" + str(self.p_cell) + "\n"
        )

        pmos_tcl = open(f"{PMOSWaffle._waffle_folder()}/waffles_pmos.tcl", "w")

        for line in pmos_data:
            pmos_tcl.write(line)
        pmos_tcl.close()

    def _update_spice_file(self):
        pmosw_spice = open("/content/pmicgen/xschem/designs/pmosw/pmosw.spice", "r")
        pmos_data = []

        for line in pmosw_spice:
            pmos_data.append(line)
        pmosw_spice.close()

        pmos_data[10] = f".param mul = {self.mult}"

        pmosw_spice = open("/content/pmicgen/xschem/designs/pmosw/pmosw.spice", "w")
        for line in pmos_data:
            pmosw_spice.write(line)
        pmosw_spice.close()

    def generate(self):
        self._update_tcl_file()
        self._update_spice_file()

        proc = subprocess.Popen(
                    [
                        "magic",
                        "-dnull",
                        "-noconsole",
                        "-rcfile",
                        "/root/.volare/libs.tech/magic/sky130A.magicrc",
                        "/content/pmicgen/magic/moswaffle/waffles_pmos.tcl",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd="/content/pmicgen/magic/moswaffle",
                    env=os.environ,
                    universal_newlines=True,
                )

        path = Path("build/sky130_pmosw/gds")
        path.mkdir(parents=True, exist_ok=True)

        proc.stdin.write("gds write ../../build/sky130_pmosw/gds/pmosw.gds\n")
        proc.stdin.write("quit -noprompt\n")

        proc.communicate()


PassTransistor = PMOSWaffle

"""TODO: Finalize NMOS variant"""


class NMOSWaffle(LDOComponent):
    def generate(self):
        nmos_tcl = open("input_files/mag_files/waffles_nmos.tcl", "r")
        nmos_data = []

        for line in nmos_tcl:
            nmos_data.append(line)
        nmos_tcl.close()

        nmos_data[12] = "set n " + str(self.n_cell) + "\n"
        nmos_data[41] = (
            "save input_files/mag_files/nmos_waffle_"
            + str(self.n_cell)
            + "x"
            + str(self.n_cell)
            + "\n"
        )
        nmos_data[42] = (
            "load input_files/mag_files/nmos_waffle_"
            + str(self.n_cell)
            + "x"
            + str(self.n_cell)
            + "\n"
        )
        nmos_data[-12] = (
            "save input_files/mag_files/POSTLAYOUT/nmos_flat_"
            + str(self.n_cell)
            + "x"
            + str(self.n_cell)
            + "\n"
        )
        nmos_data[-21] = (
            "load nmos_flat_" + str(self.n_cell) + "x" + str(self.n_cell) + "\n"
        )
        nmos_data[-22] = (
            "flatten nmos_flat_" + str(self.n_cell) + "x" + str(self.n_cell) + "\n"
        )

        nmos_tcl = open("input_files/mag_files/waffles_nmos.tcl", "w")

        for line in nmos_data:
            nmos_tcl.write(line)
        nmos_tcl.close()
