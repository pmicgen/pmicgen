def open_loop_macromodel_generation():
    pass

def closed_loop_mna():
    closed_loop_sym_mna = symbolic_mna()
    closed_loop_sym_mna.netlist = "/tmp/ldo_macromodel.spice"
    A = closed_loop_sym_mna.build()
    return A

def open_loop_mna():
    open_loop_sym_mna = symbolic_mna()
    open_loop_sym_mna.netlist = "/tmp/ldo_macromodel_openloop.spice"
    B = open_loop_sym_mna.build()
    return B