import sympy as sym
from gmid.mosplot import LoadMosfet
import numpy as np

class Transistor():
    def __init__(self, model, gm, gds, cgs, cgd):
        self.model = model
        self.gm = gm
        self.gds = gds
        self.cgs = cgs
        self.cgd = cgd


def get_G_matrix(M_1a, M_1b, M_2a, M_2b, M_4a, M_4b, r1, r2):

    gm_1a, gds_1a = (M_1a.gm, M_1a.gds)
    gm_1b, gds_1b = (M_1b.gm, M_1b.gds)
    gm_2a, gds_2a = (M_2a.gm, M_2a.gds)
    gm_2b, gds_2b = (M_2b.gm, M_2b.gds)
    gm_1 = sym.Symbol('gm_3')
    gds_1 = sym.Symbol('gds_3') 
    gm_4a, gds_4a = (M_4a.gm, M_4a.gds)
    gm_4b, gds_4b = (M_4b.gm, M_4b.gds)
    
    G = sym.Matrix(([gds_2a+gds_2b+gm_2a+gm_2b+gds_1+gm_1, -gds_2a-gm_2a-gm_2b, -gds_2b-gm_1, 0, 0, 0, 0, -1, 0, -gds_1]
               ,[-gds_2a-gm_2a, gds_2a+gds_1a+gm_2a, 0, -gds_1a-gm_1a, 0, gm_1a, 0, 0, 0, 0]
               ,[-gds_2b-gm_2b, +gm_2b, gds_2b+gds_1b, -gds_1b-gm_1b, +gm_1b, 0, 0, 0, 0, 0]
               ,[0, -gds_1a, -gds_1b, gds_1a+gds_1b+gm_1b+gm_1a+gds_4b, -gm_1b, -gm_1a, gm_4b, 0, 0, 0]
               ,[0, 0, 0, 0, 1/r1+1/r2, 0, 0, 0, 0, -1/r1]
               ,[0, 0, 0, 0, 0, 0, 0, 0, -1, 0]
               ,[0, 0, 0, 0, 0, 0, +gds_4a+gm_4a, 0, 0, 0]
               ,[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
               ,[0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
               ,[-gds_1-gm_1, 0, +gm_1, 0, -1/r1, 0, 0, 0, 0, gds_1+1/r1]))
    return G

def get_G_matrix_2(M_1a, M_1b, M_2a, M_2b, M_4a, M_4b, r1, r2):

    gm_1a, gds_1a = (M_1a.gm, M_1a.gds)
    gm_1b, gds_1b = (M_1b.gm, M_1b.gds)
    gm_2a, gds_2a = (M_2a.gm, M_2a.gds)
    gm_2b, gds_2b = (M_2b.gm, M_2b.gds)
    gm_3 = sym.Symbol('gm_3')
    gds_3 = sym.Symbol('gds_3') 
    gm_4a, gds_4a = (M_4a.gm, M_4a.gds)
    gm_4b, gds_4b = (M_4b.gm, M_4b.gds)
    
    G = sym.Matrix(([gds_2b+gds_2a+gds_3+gm_2a+gm_2b+gm_3, -gds_2a-gm_2b-gm_2a, -gds_2b-gm_3, 0, 0, 0 ,0 , -gds_3, -1, 0]
               ,[-gds_2a-gm_2a, gds_2a+gds_1a+gm_2a, 0, -gds_1a-gm_1a, 0, gm_1a, 0, 0, 0, 0]
               ,[-gds_2b-gm_2b, gm_2b, gds_2b+gds_1b, -gds_1b-gm_1b, gm_1b, 0, 0, 0, 0, 0]
               ,[0, -gds_1a, -gds_1b, gds_1a+gds_1b+gds_4b+gm_1a+gm_1b, -gm_1b, -gm_1a, gm_4b, 0, 0, 0]
               ,[0, 0, 0, 0, 1/r1+1/r2, 0, 0, -1/r1, 0, 0]
               ,[0, 0, 0, 0, 0, 0, 0, 0, 0, -1]
               ,[0, 0, 0, 0, 0, 0, gds_4a+gm_4a, 0, 0, 0]
               ,[-gds_3-gm_3, 0, gm_3, 0, -1/r1, 0, 0, gds_3+1/r1, 0, 0]
               ,[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
               ,[0, 0, 0, 0, 0, 1, 0, 0, 0, 0]))
    return G

def get_C_matrix(M_1a, M_1b, M_2a, M_2b, M_4a, M_4b, r1, r2):

    s = sym.Symbol('s')
    
    zgs_1a, zgd_1a = (1/(s*M_1a.cgs), 1/(s*M_1a.cgd))
    zgs_1b, zgd_1b = (1/(s*M_1b.cgs), 1/(s*M_1b.cgd))
    zgs_2a, zgd_2a = (1/(s*M_2a.cgs), 1/(s*M_2a.cgd))
    zgs_2b, zgd_2b = (1/(s*M_2b.cgs), 1/(s*M_2b.cgd))
    zgs_4a, zgd_4a = (1/(s*M_4a.cgs), 1/(s*M_4a.cgd))
    zgs_4b, zgd_4b = (1/(s*M_4b.cgs), 1/(s*M_4b.cgd))

    cgs_3 = sym.Symbol('cgs_3')
    cgd_3 = sym.Symbol('cgd_3')
    zgs_3 = 1/(s*cgs_3)
    zgd_3 = 1/(s*cgd_3)
    
    C = sym.Matrix(([1/zgs_2a+1/zgs_2b+1/zgs_3, -1/zgs_2a-1/zgs_2b, -1/zgs_3, 0, 0, 0, 0, 0, 0, 0]
               ,[-1/zgs_2a-1/zgs_2b, 1/zgs_2a+1/zgs_2b+1/zgd_2b+1/zgd_1a, -1/zgd_2b, 0, 0, -1/zgd_1a, 0, 0, 0, 0]
               ,[-1/zgs_3, -1/zgd_2b, 1/zgs_3+1/zgd_1b+1/zgd_3+1/zgd_2b, 0, -1/zgd_1b, 0, 0, 0, 0, -1/zgd_3]
               ,[0, 0, 0, 1/zgs_1a+1/zgs_1b+1/zgd_4b, -1/zgs_1b, -1/zgs_1a, -1/zgd_4b, 0, 0, 0]
               ,[0, 0, -1/zgd_1b, -1/zgs_1b, +1/zgd_1b+1/zgs_1b, 0, 0, 0, 0, 0]
               ,[0, -1/zgd_1a, 0, -1/zgs_1a, 0, 1/zgs_1a+1/zgd_1a, 0, 0, -1, 0]
               ,[0, 0, 0, -1/zgd_4b, 0, 0, 1/zgd_4b+1/zgs_4b+1/zgs_4a, 0, 0, 0]
               ,[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
               ,[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
               ,[0, 0, -1/zgd_3, 0, 0, 0, 0, 0, 0, 1/zgd_3]))
    return C

def get_openloop_G_matrix(M_1a, M_1b, M_2a, M_2b, M_4a, M_4b, r1, r2):

    gm_1a, gds_1a = (M_1a.gm, M_1a.gds)
    gm_1b, gds_1b = (M_1b.gm, M_1b.gds)
    gm_2a, gds_2a = (M_2a.gm, M_2a.gds)
    gm_2b, gds_2b = (M_2b.gm, M_2b.gds)
    gm_3 = sym.Symbol('gm_3')
    gds_3 = sym.Symbol('gds_3') 
    gm_4a, gds_4a = (M_4a.gm, M_4a.gds)
    gm_4b, gds_4b = (M_4b.gm, M_4b.gds)

    C = sym.Matrix(([gds_2a+gds_1a+gm_2a, 0, -gds_1a-gm_1a, 0, 0, 0, 0, 0]
               ,[+gm_2b, gds_2b+gds_1b, -gds_1b-gm_1b, gm_1b, 0, 0, 0, 0]
               ,[-gds_1a, -gds_1b, gds_1a+gds_1b+gds_4b+gm_1a+gm_1b, -gm_1b, gm_4b, 0, 0, 0]
               ,[0, 0, 0, 0, 0, 0, 0, -1]
               ,[0, 0, 0, 0, gds_4a+gm_4a, 0, 0, 0]
               ,[0, gm_3, 0, 0, 0, gds_3+1/r1, -1/r1, 0]
               ,[0, 0, 0, 0, 0, -1/r1, 1/r1+1/r2, 0]
               ,[0, 0, 0, 1, 0, 0, 0, 0]))

    return C

def get_openloop_C_matrix(M_1a, M_1b, M_2a, M_2b, M_4a, M_4b, r1, r2, cl):

    s = sym.Symbol('s')
    
    zgs_1a, zgd_1a = (1/(s*M_1a.cgs), 1/(s*M_1a.cgd))
    zgs_1b, zgd_1b = (1/(s*M_1b.cgs), 1/(s*M_1b.cgd))
    zgs_2a, zgd_2a = (1/(s*M_2a.cgs), 1/(s*M_2a.cgd))
    zgs_2b, zgd_2b = (1/(s*M_2b.cgs), 1/(s*M_2b.cgd))
    zgs_4a, zgd_4a = (1/(s*M_4a.cgs), 1/(s*M_4a.cgd))
    zgs_4b, zgd_4b = (1/(s*M_4b.cgs), 1/(s*M_4b.cgd))

    zgl = 1/(s*cl)
    
    cgs_3 = sym.Symbol('cgs_3')
    cgd_3 = sym.Symbol('cgd_3')
    zgs_3 = 1/(s*cgs_3)
    zgd_3 = 1/(s*cgd_3)
    
    C = sym.Matrix(([1/zgs_2a+1/zgd_1a+1/zgs_2b+1/zgd_2b, -1/zgd_2b, 0, 0, 0, 0, 0, 0]
               ,[-1/zgd_2b, 1/zgd_2b+1/zgd_1b+1/zgs_3+1/zgd_3, 0, -1/zgd_1b, 0, -1/zgd_3, 0, 0]
               ,[0, 0, 1/zgs_1a+1/zgs_1b+1/zgd_4b, -1/zgs_1b, -1/zgd_4b, 0, 0, 0]
               ,[0, -1/zgd_1b, -1/zgs_1b, 1/zgd_1b+1/zgs_1b, 0, 0, 0, 0]
               ,[0, 0, -1/zgd_4b, 0, 1/zgs_4a+1/zgs_4b+1/zgd_4b, 0, 0, 0]
               ,[0, -1/zgd_3, 0, 0, 0, 1/zgd_3+1/zgl, 0, 0]
               ,[0, 0, 0, 0, 0, 0, 0, 0]
               ,[0, 0, 0, 0, 0, 0, 0, 0]))

    return C

class Exploration_Transistor():
        def __init__(self, model=None):
            self.model = model

def pass_transistor_exploration(lookup_table, Vdd, Vreg, il, R1, R2, lengths, gmid_sweep):
    
    ## First create generic pmos mosfet, for this we should consider:
    ## 1. the vds value the drop voltage from vdd to vreg.
    pt_lutable = LoadMosfet(lookup_table=lookup_table, mos="pmos", vsb=0, vds=-(Vdd-Vreg), vgs=(-1.8, -0.6, 0.1), lengths = lengths)
    
    ## Creacion de transistor
    pass_transistor = Exploration_Transistor()
    
    ## pass transistor drain current.
    pass_transistor.id = il+Vreg/(R1+R2)
    
    ### Vgs con barrido en Gm/id para distintos L
    pass_transistor.vgs = pt_lutable.interpolate(
                x_expression=pt_lutable.lengths_expression,
                x_value=lengths,
                y_expression=pt_lutable.gmid_expression,
                y_value=gmid_sweep,
                z_expression=pt_lutable.vgs_expression,
            )
    ### Jd con barrido en Vgs para distintos L
    pass_transistor.Jd = []
    for idx, x in enumerate(lengths):
        temp = pt_lutable.interpolate(
                    x_expression=pt_lutable.lengths_expression,
                    x_value=x,
                    y_expression=pt_lutable.vgs_expression,
                    y_value=pass_transistor.vgs[idx,:],
                    z_expression=pt_lutable.current_density_expression,
                )
        pass_transistor.Jd.append(temp)
    pass_transistor.Jd = np.vstack(pass_transistor.Jd)
    
    ### Gm con barrido en Vgs para distintos L
    pass_transistor.gm = []
    for idx, x in enumerate(lengths):
        temp = pt_lutable.interpolate(
                    x_expression=pt_lutable.lengths_expression,
                    x_value=x,
                    y_expression=pt_lutable.vgs_expression,
                    y_value=pass_transistor.vgs[idx,:],
                    z_expression=pt_lutable.gm_expression,
                )
        pass_transistor.gm.append(temp)
    pass_transistor.gm = np.vstack(pass_transistor.gm)
    
    ### Gds con barrido en Vgs para distintos L
    pass_transistor.gds = []
    for idx, x in enumerate(lengths):
        temp = pt_lutable.interpolate(
                    x_expression=pt_lutable.lengths_expression,
                    x_value=x,
                    y_expression=pt_lutable.vgs_expression,
                    y_value=pass_transistor.vgs[idx,:],
                    z_expression=pt_lutable.gds_expression,
                )
        pass_transistor.gds.append(temp)
    pass_transistor.gds = np.vstack(pass_transistor.gds)

    ## W depending on the load current
    pass_transistor.W = np.divide(pass_transistor.id, pass_transistor.Jd)
    
    ### Cgd con barrido en Vgs para distintos L
    pass_transistor.cgd = []
    for idx, x in enumerate(lengths):
        temp = pt_lutable.interpolate(
                    x_expression=pt_lutable.lengths_expression,
                    x_value=x,
                    y_expression=pt_lutable.vgs_expression,
                    y_value=pass_transistor.vgs[idx,:],
                    z_expression=pt_lutable.cgd_expression,
                )
        pass_transistor.cgd.append(temp)
    pass_transistor.cgd = np.vstack(pass_transistor.cgd)
    
    ### Cgs con barrido en Vgs para distintos L
    pass_transistor.cgs = []
    for idx, x in enumerate(lengths):
        temp = pt_lutable.interpolate(
                    x_expression=pt_lutable.lengths_expression,
                    x_value=x,
                    y_expression=pt_lutable.vgs_expression,
                    y_value=pass_transistor.vgs[idx,:],
                    z_expression=pt_lutable.cgs_expression,
                )
        pass_transistor.cgs.append(temp)
    pass_transistor.cgs = np.vstack(pass_transistor.cgs)
    
    return pass_transistor

## Get phase margin, could be improved.
def get_PM(s_sweep, G, C_lamb, B, index, L, eq, cgs, cgd):
    
    #bode_data = []
    #phase_data = []

    """
    s_sweep = np.logspace(0, 10, num=200, base=10)
    PSRR = [(np.linalg.inv(G+C_lamb(cgs, cgd, s*1j))*B)[6] for s in s_sweep]
    magnitude = 20*np.log10((np.abs(PSRR)).astype(float))

    print(magnitude)

    return 0
    """

    s = 0.1
    for i in range(50):
        PSRR = (np.linalg.inv(G+C_lamb(cgs, cgd, s*1j))*B)[eq]
        magnitude = 20*np.log10(float(np.abs(PSRR)))
        #print(magnitude)
        #print(s)
        if np.abs(magnitude)>5:
            next_s = s*(np.abs(magnitude)*0.3)
            #bode_data.append(magnitude)
            #phase_data.append(math.phase(PSRR))
        else:
            #print("END mag",magnitude)
            #print("END phase",(180/np.pi)*math.phase(PSRR))
            return (180/np.pi)*math.phase(PSRR)
        s = next_s
        
    return 0