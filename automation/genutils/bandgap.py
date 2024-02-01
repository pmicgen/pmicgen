from .component import *

class BGR(LDOComponent):
    def generate():
        proc = subprocess.run(
            [
                "magic",
                "-dnull",
                "-noconsole",
                f"-rcfile {self.tech.magicrc_path()}",
                f"{PMOSWaffle._waffle_folder()}/waffles_pmos.tcl",
            ],
            cwd=PMOSWaffle._waffle_folder(),
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )