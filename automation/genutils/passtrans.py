from .component import *
import pathlib
import subprocess
import sys

class PMOSWaffle(LDOComponent):
    p_cell: int

    def __init__(self, tech: TechManager, p_cell: int) -> None:
        super().__init__(tech)
        self.p_cell = p_cell

    def _waffle_folder() -> str:
        return f"{pathlib.Path(__file__).parent.parent.resolve()}/magic/moswaffle"

    def _update_tcl_file(self) -> None:
        pmos_tcl = open(
            f"{PMOSWaffle._waffle_folder()}/waffles_pmos.tcl", "r"
        )
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

    """TODO: Fix process run"""
    def generate(self):
        self._update_tcl_file()
        proc = subprocess.run(
            [
                "/bin/magic",
                "-dnull",
                "-dnoconsole",
                f"-rcfile {self.tech.magicrc_path()}",
                f"{PMOSWaffle._waffle_folder()}/waffles_pmos.tcl",
            ],
            cwd=PMOSWaffle._waffle_folder(),
        )
        print(proc)


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
