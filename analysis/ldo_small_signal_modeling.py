class small_signal_device():
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

class small_signal_macromodel():
    def __init__(self,macromodel_file_path):
        self.macromodel_file_path = macromodel_file_path
    
    def build(self, template, op_data, nodes):
        small_signal_devices = []
        for device in template.devices:

            if(device.model=='sky130_fd_pr__nfet_01v8_lvt'):
                small_signal_devices.append(small_signal_device(name=device.name, 
                                                            gds=op_data[f"gds_{device.name}"][0], 
                                                            gm=op_data[f"gm_{device.name}"][0],
                                                            cgs=op_data[f"cgs_{device.name}"][0], 
                                                            cgd=op_data[f"cgd_{device.name}"][0], 
                                                            vs=nodes[device.s_node], vd=nodes[device.d_node], vg=nodes[device.g_node]))
            else:
                small_signal_devices.append(small_signal_device(name=device.name, 
                                                            gds=op_data[f"gds_{device.name}"][0], 
                                                            gm=op_data[f"gm_{device.name}"][0],
                                                            cgs=op_data[f"cgs_{device.name}"][0], 
                                                            cgd=op_data[f"cgd_{device.name}"][0], 
                                                            vs=nodes[device.s_node], vd=nodes[device.d_node], vg=nodes[device.g_node]))
        f = open(self.macromodel_file_path, "w")
        for device in small_signal_devices:
            #print("\n".join(device.get_model_spice()))
            f.write("\n".join(device.get_model_spice()))
            f.write("\n")
        f.close()
        return small_signal_devices
    
    def build_openloop(self, template, op_data, nodes, node_disp):

        devices_connected = []
        device_connected = []
        for device in template.devices:
            if(device.s_node==node_disp):
                device_connected.append((device, 's_node'))
            elif(device.d_node==node_disp):
                device_connected.append((device, 's_node'))
            elif(device.g_node==node_disp):
                device_connected.append((device, 's_node'))
            devices_connected.append(device_connected)
            

        
        small_signal_devices = []
        for device in template.devices:

            if(device.model=='sky130_fd_pr__nfet_01v8_lvt'):
                small_signal_devices.append(small_signal_device(name=device.name, 
                                                            gds=op_data[f"gds_{device.name}"][0], 
                                                            gm=op_data[f"gm_{device.name}"][0],
                                                            cgs=op_data[f"cgs_{device.name}"][0], 
                                                            cgd=op_data[f"cgd_{device.name}"][0], 
                                                            vs=nodes[device.s_node], vd=nodes[device.d_node], vg=nodes[device.g_node]))
            else:
                small_signal_devices.append(small_signal_device(name=device.name, 
                                                            gds=op_data[f"gds_{device.name}"][0], 
                                                            gm=op_data[f"gm_{device.name}"][0],
                                                            cgs=op_data[f"cgs_{device.name}"][0], 
                                                            cgd=op_data[f"cgd_{device.name}"][0], 
                                                            vs=nodes[device.s_node], vd=nodes[device.d_node], vg=nodes[device.g_node]))
        f = open(self.macromodel_file_path, "w")
        for device in small_signal_devices:
            #print("\n".join(device.get_model_spice()))
            f.write("\n".join(device.get_model_spice()))
            f.write("\n")
        f.close()
        return small_signal_devices