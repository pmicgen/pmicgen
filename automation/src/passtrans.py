from component import *

class PassTransistor(LDOComponent):
    def generate():
        nmos_tcl=open('input_files/mag_files/waffles_nmos.tcl','r')
        nmos_data=[]

        for line in nmos_tcl:
            nmos_data.append(line)
        nmos_tcl.close()

        nmos_data[12]='set n '+str(n_cell)+'\n'
        nmos_data[41]='save input_files/mag_files/nmos_waffle_'+str(n_cell)+'x'+str(n_cell)+'\n'
        nmos_data[42]='load input_files/mag_files/nmos_waffle_'+str(n_cell)+'x'+str(n_cell)+'\n'
        nmos_data[-12]='save input_files/mag_files/POSTLAYOUT/nmos_flat_'+str(n_cell)+'x'+str(n_cell)+'\n'
        nmos_data[-21]='load nmos_flat_'+str(n_cell)+'x'+str(n_cell)+'\n'
        nmos_data[-22]='flatten nmos_flat_'+str(n_cell)+'x'+str(n_cell)+'\n'

        nmos_tcl=open('input_files/mag_files/waffles_nmos.tcl','w')

        for line in nmos_data:
            nmos_tcl.write(line)
        nmos_tcl.close()

        pmos_tcl=open('input_files/mag_files/waffles_pmos.tcl','r')
        pmos_data=[]

        for line in pmos_tcl:
            pmos_data.append(line)
        pmos_tcl.close()

        pmos_data[12]='set n '+str(p_cell)+'\n'
        pmos_data[30]='save input_files/mag_files/pmos_waffle_'+str(p_cell)+'x'+str(p_cell)+'\n'
        pmos_data[31]='load input_files/mag_files/pmos_waffle_'+str(p_cell)+'x'+str(p_cell)+'\n'
        pmos_data[-12]='save input_files/mag_files/POSTLAYOUT/pmos_flat_'+str(p_cell)+'x'+str(p_cell)+'\n'
        pmos_data[-21]='load pmos_flat_'+str(p_cell)+'x'+str(p_cell)+'\n'
        pmos_data[-22]='flatten pmos_flat_'+str(p_cell)+'x'+str(p_cell)+'\n'

        pmos_tcl=open('input_files/mag_files/waffles_pmos.tcl','w')

        for line in pmos_data:
            pmos_tcl.write(line)
        pmos_tcl.close()