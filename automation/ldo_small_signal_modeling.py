class small_signal_model():
    def __init__(self, name=None, gm=None, gds=None, cgs=None, cgd=None, vd=None, vs=None, vg=None):
        self.name = name
        self.gm = gm
        self.rds = 1/gds
        self.cgs = cgs
        self.cgd = cgd
        self.vd = vd
        self.vs = vs
        self.vg = vg
    def get_model_spice(self):
        model = [
            f"Gm_{self.name} {self.vd} {self.vs} {self.vg} {self.vs} {self.gm}",
            f"Rds_{self.name} {self.vs} {self.vd} {self.rds}",
            f"Cgs_{self.name} {self.vg} {self.vs} {self.cgs}",
            f"Cgd_{self.name} {self.vg} {self.vd} {self.cgd}",
        ]
        return model