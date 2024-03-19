import numpy as np
from gmid.mosplot.parsers.ngspice_parser import NgspiceRawFileReader
#from ldo_small_signal_modeling import small_signal_model
import os

class template_generator():
    def __init__(
        self,
        temp=27,
        model_paths=[],
        model_names={"nmos": "NMOS_VTH", "pmos": "PMOS_VTH"},
        description="gmid lookup table",
        raw_spice="",
        devices=[],
        output_file_path="",
        ota_netlist_path="",
        netlist_output="",
        ota_name="",
        device_params_instantiation_model ="",
        simulation_circuit = [],
        subckt_instantation = ""
    ):
        self.temp = temp
        self.model_paths = model_paths
        self.model_names = model_names
        self.description = description
        self.raw_spice = raw_spice
        self.lookup_table = {}
        self.devices = devices
        self.output_file_path = output_file_path
        self.ota_netlist_path = ota_netlist_path
        self.netlist_output = netlist_output
        self.ota_name = ota_name
        self.device_params_instantiation_model = device_params_instantiation_model
        self.simulation_circuit = simulation_circuit
        self.subckt_instantation = subckt_instantation

    def ngspice_parameters(self):
        self.identifier = "nmos"
        self.parameter_table = {}
        for idx, device in enumerate(self.devices):
            
            device_parameter_table = {
                # parameter name : [name recognized by simulator, name used in the output file],
                "gm_"+device.name.lower()   : ["save @m.x1."+device.name+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[gm]"   , "@m.x1."+device.name.lower()+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[gm]"],
                "gds_"+device.name.lower()  : ["save @m.x1."+device.name+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[gds]"  , "@m.x1."+device.name.lower()+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[gds]"],
                "cgs_"+device.name.lower()  : ["save @m.x1."+device.name+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[cgs]"  , "@m.x1."+device.name.lower()+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[cgs]"],
                "cgd_"+device.name.lower()  : ["save @m.x1."+device.name+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[cgd]"  , "@m.x1."+device.name.lower()+"."+self.device_params_instantiation_model.format(device_model=device.model)+"[cgd]"],
            }

            self.parameter_table.update(device_parameter_table)

        self.save_internal_parameters = "\n".join([values[0] for values in self.parameter_table.values()])
        return self.save_internal_parameters

    def ngspice_simulator_setup(self):
        self.ngspice_parameters()
        simulator = [
            f".options TEMP = {self.temp}",
            f".options TNOM = {self.temp}",
            ".param CM_VOLTAGE = 0.8",
            ".param OUTPUT_VOLTAGE = 0.7",
            ".control",
            self.save_internal_parameters,
            "ac dec 200 10 1000Meg",
            "settype decibel out",
            "*plot vdb(out)",
            "let phase_val = 180/PI*cph(out)",
            "settype phase phase_val",
            "*plot phase_val",
            "meas ac phase_margin find phase_margin_val when vdb(out)=0",
            "meas ac crossover_freq WHEN vdb(out)=0",
            "op",
            f"write {self.output_file_path} all",
            ".endc",
        ]
        return simulator
    
    def generate_netlist(self):
        if self.model_paths:
            include_string = "\n".join([path for path in self.model_paths])
        else:
            include_string = ""

        if self.simulation_circuit:
            include_circuit = "\n".join([line for line in self.simulation_circuit])
        else:
            include_circuit = ""

        circuit = [
            "* Lookup Table Generation *",
            include_string,
            include_circuit,
            self.subckt_instantation.format(subckt=self.ota_name),
            self.raw_spice,
        ]
        return circuit
    
    def print_netlist(self, subckt):
        #self.r = 1
        #self.identifier = "nmos"
        circuit = self.generate_netlist()
        self.ngspice_parameters()
        simulator = self.ngspice_simulator_setup()
        circuit.extend(simulator)
        circuit.extend(subckt)
        print("---------------------------------------------------")
        print("----- This is the netlist that gets simulated -----")
        print("---------------------------------------------------")
        print("\n".join(circuit))
        print("---------------------------------------------------")
        print("")
        #f = open("automation/ota_simulation_generated.spice", "w")
        #f.write("\n".join(circuit))
        #f.close()
        return circuit

    def build(self):
        ota_netlist = open(self.ota_netlist_path, "r")

        self.devices = get_devices(ota_netlist)
        ota_netlist.seek(0)

        ota_netlist_as_subckt = open("temp.spice", "w")
        for idx, line in enumerate(ota_netlist.readlines()):
            if(line[0:9]=="**.subckt"):
                print("subck")
                ota_netlist_as_subckt.write(line[2:])
            elif(line=="**.ends\n"):
                ota_netlist_as_subckt.write(".ends\n")
            else:
                ota_netlist_as_subckt.write(line)
        ota_netlist_as_subckt.close()
        ota_netlist.close()

        ota_netlist_as_subckt = open("temp.spice", "r")

        netlist = self.print_netlist([line.strip() for line in ota_netlist_as_subckt.readlines()])

        f = open(self.netlist_output, "w")
        f.write("\n".join(netlist))
        f.close()

        os.remove("temp.spice")
    

class device():
    def __init__(self, name=None, model=None, W=None, L=None, n=None, m=None, d_node=None, s_node=None, g_node=None, b_node=None):
        self.name = name
        self.W = W
        self.L = L
        self.n = n
        self.m = m
        self.d_node = d_node
        self.s_node = s_node
        self.g_node = g_node
        self.b_node = b_node
        self.model = model

def get_devices(netlist):    
    clean_netlist = []
    for idx, line in enumerate(netlist.readlines()):
        if(line[0]!="*" and line[0]!="."):
            clean_netlist.append(line)

    devices = []
    for idx, line in enumerate(clean_netlist):
        if (line[0:2]=="XM"):
            params = line.split(" ")
            devices.append(device(name = params[0].lower(), model = params[5], d_node=params[1], g_node=params[2], s_node=params[3], b_node=params[4]))
    
    return devices

def __save_ngspice_parameters(self, analysis, mos, length, vsb):
        column_names = analysis[0].dtype.names
        data = analysis[0]

        for p in self.parameter_table.keys():
            col_name = self.parameter_table[p][1]
            if col_name in column_names:
                res = np.array(data[col_name])
                self.lookup_table[self.identifier][p][length][vsb] = res.reshape(self.n_vgs, self.n_vds)

class ota_op():
    def __init__(
            self,
            ota_netlist_path="",
            ota_simulation_template_path="",
            ):
        self.ota_netlist_path = ota_netlist_path
        self.ota_simulation_template_path = ota_simulation_template_path