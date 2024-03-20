from gmid.mosplot.parsers.ngspice_parser import NgspiceRawFileReader

def op_parser(template):
    ars, _ = NgspiceRawFileReader().read_file(template.output_file_path)

    column_names = ars[0].dtype.names
    data = ars[0]

    op_data = {}
    for p in template.parameter_table.keys():
                col_name = template.parameter_table[p][1]
                if col_name in column_names:
                    op_data[p] = data[col_name]
                    
    return op_data

def node_identification(template, Vdd="VDD", Vss="VSS", out="OUT", in_pos="IN_P", in_neg="IN_M"):
    nodes = {}
    node_num = 4
    for device in template.devices:
        for node in [device.d_node, device.s_node, device.g_node]:
            if (node==Vss) and node not in nodes:
                nodes[node]=0                                  #Vss and in_neg set to ground
            elif (node==in_neg) and node not in nodes:
                nodes[node]=3   
            elif node==Vdd and node not in nodes:
                nodes[node]=1
            elif node==out and node not in nodes:
                nodes[node]=2   
            elif node not in nodes:
                nodes[node]=node_num
                node_num+=1
    return nodes, nodes[in_pos], node_num

def node_identification_openloop(template, Vdd="VDD", Vss="VSS", out="OUT", in_pos="IN_P", in_neg="IN_M"):
    nodes = {}
    node_num = 4
    for device in template.devices:
        for node in [device.d_node, device.s_node, device.g_node]:
            if (node==Vss or node==in_neg) and node not in nodes:
                nodes[node]=0                                       #Vss and in_neg set to ground
            elif node==Vdd and node not in nodes:
                nodes[node]=0
            elif node==out and node not in nodes:
                nodes[node]=2
            elif node==in_pos and node not in nodes:
                nodes[node]=3
            elif node not in nodes:
                nodes[node]=node_num
                node_num+=1
    return nodes, nodes[in_pos], node_num

class Ldo():
    def __init__(self, psr_condition, load_regulation_condition, pm_condition, area_condition):
        optimize = {}
        if psr_condition=="min":
            self.psr_condition = float('inf')
            optimize["psr_condition"]="min"
        else:
            self.psr_condition = psr_condition

        if load_regulation_condition=="min":
            self.load_regulation_condition = float('inf')
            optimize["load_regulation_condition"]="min"
        else:
            self.load_regulation_condition = load_regulation_condition

        if pm_condition=="max":
            self.pm_condition = float('-inf')
            optimize["pm_condition"]="max"
        else:
            self.pm_condition = pm_condition

        if area_condition=="min":
            self.area_condition = float('inf')
            optimize["area_condition"]="min"
        else:
            self.area_condition = area_condition

        self.optimize = optimize
