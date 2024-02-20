import os
from sympy import *
import numpy as np
import pandas as pd
init_printing()

class symbolic_mna():
    def __init__(
            self,
            netlist=""
            ):
        self.netlist = netlist

    def __pre_processing(self):

        fd1 = open(self.netlist,'r')
        self.content = fd1.readlines()
        self.content = [x.strip() for x in self.content]  #remove leading and trailing white space
        # remove empty lines
        while '' in self.content:
            self.content.pop(self.content.index(''))

        # remove comment lines, these start with a asterisk *
        self.content = [n for n in self.content if not n.startswith('*')]
        # remove other comment lines, these start with a semicolon ;
        self.content = [n for n in self.content if not n.startswith(';')]
        # remove spice directives, these start with a period, .
        self.content = [n for n in self.content if not n.startswith('.')]
        # converts 1st letter to upper case
        #self.content = [x.upper() for x in self.content] <- this converts all to upper case
        self.content = [x.capitalize() for x in self.content]
        # removes extra spaces between entries
        self.content = [' '.join(x.split()) for x in self.content]

        self.line_cnt = len(self.content) # number of lines in the netlist
        self.branch_cnt = 0  # number of branches in the netlist
        # check number of entries on each line, count each element type
        for i in range(self.line_cnt):
            x = self.content[i][0]
            tk_cnt = len(self.content[i].split()) # split the line into a list of words

            if (x == 'R') or (x == 'L') or (x == 'C'):
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                self.num_rlc += 1
                self.branch_cnt += 1
                if x == 'L':
                    self.num_ind += 1
            elif x == 'V':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                self.num_v += 1
                self.branch_cnt += 1
            elif x == 'I':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                self.num_i += 1
                self.branch_cnt += 1
            elif x == 'O':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                self.num_opamps += 1
            elif x == 'E':
                if (tk_cnt != 6):
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 6".format(tk_cnt))
                self.num_vcvs += 1
                self.branch_cnt += 1
            elif x == 'G':
                if (tk_cnt != 6):
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 6".format(tk_cnt))
                self.num_vccs += 1
                self.branch_cnt += 1
            elif x == 'F':
                if (tk_cnt != 5):
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 5".format(tk_cnt))
                self.num_cccs += 1
                self.branch_cnt += 1
            elif x == 'H':
                if (tk_cnt != 5):
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 5".format(tk_cnt))
                self.num_ccvs += 1
                self.branch_cnt += 1
            elif x == 'K':
                if (tk_cnt != 4):
                    print("branch {:d} not formatted correctly, {:s}".format(i,self.content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                self.num_cpld_ind += 1
            else:
                print("unknown element type in branch {:d}, {:s}".format(i,self.content[i]))

    def __parser(self):
        # build the pandas data frame
        self.df = pd.DataFrame(columns=['element','p node','n node','cp node','cn node',
            'Vout','value','Vname','Lname1','Lname2'])

        # this data frame is for branches with unknown currents
        self.df2 = pd.DataFrame(columns=['element','p node','n node'])

        # load branch info into data frame  
        for i in range(self.line_cnt):
            x = self.content[i][0]

            if (x == 'R') or (x == 'L') or (x == 'C'):
                self.rlc_element(i)
            elif (x == 'V') or (x == 'I'):
                self.indep_source(i)
            elif x == 'O':
                self.opamp_sub_network(i)
            elif x == 'E':
                self.vcvs_sub_network(i)
            elif x == 'G':
                self.vccs_sub_network(i)
            elif x == 'F':
                self.cccs_sub_network(i)
            elif x == 'H':
                self.ccvs_sub_network(i)
            elif x == 'K':
                self.cpld_ind_sub_network(i)
            else:
                print("unknown element type in branch {:d}, {:s}".format(i,self.content[i]))

        # Check for position of voltages sources in the dataframe.
        source_index = [] # keep track of voltage source row number
        other_index = [] # make a list of all other types
        for i in range(len(self.df)):
            # process all the elements creating unknown currents
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if (x == 'V'):
                source_index.append(i)
            else:
                other_index.append(i)

        self.df = self.df.reindex(source_index+other_index,copy=True) # re-order the data frame
        self.df.reset_index(drop=True, inplace=True) # renumber the index

        # count number of nodes
        self.num_nodes = self.count_nodes()

        # Build df2: consists of branches with current unknowns, used for C & D matrices
        # walk through data frame and find these parameters
        count = 0
        for i in range(len(self.df)):
            # process all the elements creating unknown currents
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if (x == 'L') or (x == 'V') or (x == 'O') or (x == 'E') or (x == 'H') or (x == 'F'):
                self.df2.loc[count,'element'] = self.df.loc[i,'element']
                self.df2.loc[count,'p node'] = self.df.loc[i,'p node']
                self.df2.loc[count,'n node'] = self.df.loc[i,'n node']
                count += 1

    def __print_netlist_report(self):
        # print a report
        print('Net list report')
        print('number of lines in netlist: {:d}'.format(self.line_cnt))
        print('number of branches: {:d}'.format(self.branch_cnt))
        print('number of nodes: {:d}'.format(self.num_nodes))
        # count the number of element types that affect the size of the B, C, D, E and J arrays
        # these are current unknows
        self.i_unk = self.num_v+self.num_opamps+self.num_vcvs+self.num_ccvs+self.num_cccs+self.num_ind
        print('number of unknown currents: {:d}'.format(self.i_unk))
        print('number of RLC (passive components): {:d}'.format(self.num_rlc))
        print('number of inductors: {:d}'.format(self.num_ind))
        print('number of independent voltage sources: {:d}'.format(self.num_v))
        print('number of independent current sources: {:d}'.format(self.num_i))
        print('number of op amps: {:d}'.format(self.num_opamps))
        print('number of E - VCVS: {:d}'.format(self.num_vcvs))
        print('number of G - VCCS: {:d}'.format(self.num_vccs))
        print('number of F - CCCS: {:d}'.format(self.num_cccs))
        print('number of H - CCVS: {:d}'.format(self.num_ccvs))
        print('number of K - Coupled inductors: {:d}'.format(self.num_cpld_ind))

    def indep_source(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'value'] = float(tk[3])

    # loads passive elements into branch structure
    def rlc_element(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'value'] = np.format_float_scientific(np.float32(tk[3]))

    # loads multi-terminal elements into branch structure
    # O - Op Amps
    def opamp_sub_network(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'Vout'] = int(tk[3])

    # G - VCCS
    def vccs_sub_network(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'cp node'] = int(tk[3])
        self.df.loc[line_nu,'cn node'] = int(tk[4])
        self.df.loc[line_nu,'value'] = np.format_float_scientific(float(tk[5]))

    # E - VCVS
    # in sympy E is the number 2.718, replacing E with Ea otherwise, sympify() errors out
    def vcvs_sub_network(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0].replace('E', 'Ea')
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'cp node'] = int(tk[3])
        self.df.loc[line_nu,'cn node'] = int(tk[4])
        self.df.loc[line_nu,'value'] = float(tk[5])

    # F - CCCS
    def cccs_sub_network(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'Vname'] = tk[3].capitalize()
        self.df.loc[line_nu,'value'] = float(tk[4])

    # H - CCVS
    def ccvs_sub_network(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'p node'] = int(tk[1])
        self.df.loc[line_nu,'n node'] = int(tk[2])
        self.df.loc[line_nu,'Vname'] = tk[3].capitalize()
        self.df.loc[line_nu,'value'] = float(tk[4])

    # K - Coupled inductors
    def cpld_ind_sub_network(self, line_nu):
        tk = self.content[line_nu].split()
        self.df.loc[line_nu,'element'] = tk[0]
        self.df.loc[line_nu,'Lname1'] = tk[1].capitalize()
        self.df.loc[line_nu,'Lname2'] = tk[2].capitalize()
        self.df.loc[line_nu,'value'] = float(tk[3])

    # function to scan self.df and get largest node number
    def count_nodes(self):
        # need to check that nodes are consecutive
        # fill array with node numbers
        p = np.zeros(self.line_cnt+1)
        for i in range(self.line_cnt):
            # need to skip coupled inductor 'K' statements
            if self.df.loc[i,'element'][0] != 'K': #get 1st letter of element name
                p[self.df['p node'][i]] = self.df['p node'][i]
                p[self.df['n node'][i]] = self.df['n node'][i]

        # find the largest node number
        if self.df['n node'].max() > self.df['p node'].max():
            largest = self.df['n node'].max()
        else:
            largest =  self.df['p node'].max()

        largest = int(largest)
        # check for unfilled elements, skip node 0
        for i in range(1,largest):
            if p[i] == 0:
                print('nodes not in continuous order, node {:.0f} is missing'.format(p[i-1]+1))

        return largest

    def __init_matrix(self):
        # initialize some symbolic matrix with zeros
        # A is formed by [[G, C] [B, D]]
        # Z = [I,E]
        # X = [V, J]
        self.V = zeros(self.num_nodes,1)
        self.I = zeros(self.num_nodes,1)
        self.G = zeros(self.num_nodes,self.num_nodes)  # also called Yr, the reduced nodal matrix
        self.s = Symbol('s')  # the Laplace variable

        # count the number of element types that affect the size of the B, C, D, E and J arrays
        # these are element types that have unknown currents
        self.i_unk = self.num_v+self.num_opamps+self.num_vcvs+self.num_ccvs+self.num_ind+self.num_cccs
        # if self.i_unk == 0, just generate empty arrays
        self.B = zeros(self.num_nodes,self.i_unk)
        self.C = zeros(self.i_unk,self.num_nodes)
        self.D = zeros(self.i_unk,self.i_unk)
        self.Ev = zeros(self.i_unk,1)
        self.J = zeros(self.i_unk,1)

    def __G_matrix(self):
        # G matrix
        for i in range(len(self.df)):  # process each row in the data frame
            n1 = self.df.loc[i,'p node']
            n2 = self.df.loc[i,'n node']
            cn1 = self.df.loc[i,'cp node']
            cn2 = self.df.loc[i,'cn node']
            # process all the passive elements, save conductance to temp value
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if x == 'R':
                g = 1/sympify(self.df.loc[i,'element'])
            if x == 'C':
                g = self.s*sympify(self.df.loc[i,'element'])
            if x == 'G':   #vccs type element
                g = sympify(self.df.loc[i,'element'])  # use a symbol for gain value

            if (x == 'R') or (x == 'C'):
                # If neither side of the element is connected to ground
                # then subtract it from the appropriate location in the matrix.
                if (n1 != 0) and (n2 != 0):
                    self.G[n1-1,n2-1] += -g
                    self.G[n2-1,n1-1] += -g

                # If node 1 is connected to ground, add element to diagonal of matrix
                if n1 != 0:
                    self.G[n1-1,n1-1] += g

                # same for for node 2
                if n2 != 0:
                    self.G[n2-1,n2-1] += g

            if x == 'G':    #vccs type element
                # check to see if any terminal is grounded
                # then stamp the matrix
                if n1 != 0 and cn1 != 0:
                    self.G[n1-1,cn1-1] += g

                if n2 != 0 and cn2 != 0:
                    self.G[n2-1,cn2-1] += g

                if n1 != 0 and cn2 != 0:
                    self.G[n1-1,cn2-1] -= g

                if n2 != 0 and cn1 != 0:
                    self.G[n2-1,cn1-1] -= g

        #print(self.G)  # display the G matrix

    def __B_matrix(self):
        # generate the self.B Matrix
        sn = 0   # count source number as code walks through the data frame
        for i in range(len(self.df)):
            n1 = self.df.loc[i,'p node']
            n2 = self.df.loc[i,'n node']
            n_vout = self.df.loc[i,'Vout'] # node connected to op amp output
            # process elements with input to self.B matrix
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if x == 'V':
                if self.i_unk > 1:  #is self.B greater than 1 by n?, V
                    if n1 != 0:
                        self.B[n1-1,sn] = 1
                    if n2 != 0:
                        self.B[n2-1,sn] = -1
                else:
                    if n1 != 0:
                        self.B[n1-1] = 1
                    if n2 != 0:
                        self.B[n2-1] = -1
                sn += 1   #increment source count
            if x == 'O':  # op amp type, output connection of the opamp goes in the self.B matrix
                self.B[n_vout-1,sn] = 1
                sn += 1   # increment source count
            if (x == 'H') or (x == 'F'):  # H: ccvs, F: cccs,
                if self.i_unk > 1:  #is self.B greater than 1 by n?, H, F
                    # check to see if any terminal is grounded
                    # then stamp the matrix
                    if n1 != 0:
                        self.B[n1-1,sn] = 1
                    if n2 != 0:
                        self.B[n2-1,sn] = -1
                else:
                    if n1 != 0:
                        self.B[n1-1] = 1
                    if n2 != 0:
                        self.B[n2-1] = -1
                sn += 1   #increment source count
            if x == 'E':   # vcvs type, only ik column is altered at n1 and n2
                if self.i_unk > 1:  #is self.B greater than 1 by n?, E
                    if n1 != 0:
                        self.B[n1-1,sn] = 1
                    if n2 != 0:
                        self.B[n2-1,sn] = -1
                else:
                    if n1 != 0:
                        self.B[n1-1] = 1
                    if n2 != 0:
                        self.B[n2-1] = -1
                sn += 1   #increment source count
            if x == 'L':
                if self.i_unk > 1:  #is self.B greater than 1 by n?, L
                    if n1 != 0:
                        self.B[n1-1,sn] = 1
                    if n2 != 0:
                        self.B[n2-1,sn] = -1
                else:
                    if n1 != 0:
                        self.B[n1-1] = 1
                    if n2 != 0:
                        self.B[n2-1] = -1
                sn += 1   #increment source count
        # check source count
        if sn != self.i_unk:
            print('source number, sn={:d} not equal to self.i_unk={:d} in matrix self.B'.format(sn,self.i_unk))
        #print(self.B)   # display the B matrix

    def __find_vname(self, name):
        # need to walk through data frame and find these parameters
        for i in range(len(self.df2)):
            # process all the elements creating unknown currents
            if name == self.df2.loc[i,'element']:
                n1 = self.df2.loc[i,'p node']
                n2 = self.df2.loc[i,'n node']
                return n1, n2, i  # n1, n2 & col_num are from the branch of the controlling element

        print('failed to find matching branch element in find_vname')

    def __C_matrix(self):
        # find the the column position in the C and self.D matrix for controlled sources
        # needs to return the node numbers and branch number of controlling branch
        # generate the self.C Matrix
        sn = 0   # count source number as code walks through the data frame
        for i in range(len(self.df)):
            n1 = self.df.loc[i,'p node']
            n2 = self.df.loc[i,'n node']
            cn1 = self.df.loc[i,'cp node'] # nodes for controlled sources
            cn2 = self.df.loc[i,'cn node']
            n_vout = self.df.loc[i,'Vout'] # node connected to op amp output

            # process elements with input to B matrix
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if x == 'V':
                if self.i_unk > 1:  #is B greater than 1 by n?, V
                    if n1 != 0:
                        self.C[sn,n1-1] = 1
                    if n2 != 0:
                        self.C[sn,n2-1] = -1
                else:
                    if n1 != 0:
                        self.C[n1-1] = 1
                    if n2 != 0:
                        self.C[n2-1] = -1
                sn += 1   #increment source count

            if x == 'O':  # op amp type, input connections of the opamp go into the self.C matrix
                # self.C[sn,n_vout-1] = 1
                if self.i_unk > 1:  #is B greater than 1 by n?, O
                    # check to see if any terminal is grounded
                    # then stamp the matrix
                    if n1 != 0:
                        self.C[sn,n1-1] = 1
                    if n2 != 0:
                        self.C[sn,n2-1] = -1
                else:
                    if n1 != 0:
                        self.C[n1-1] = 1
                    if n2 != 0:
                        self.C[n2-1] = -1
                sn += 1   # increment source count

            if x == 'F':  # need to count F (cccs) types
                sn += 1   #increment source count
            if x == 'H':  # H: ccvs
                if self.i_unk > 1:  #is B greater than 1 by n?, H
                    # check to see if any terminal is grounded
                    # then stamp the matrix
                    if n1 != 0:
                        self.C[sn,n1-1] = 1
                    if n2 != 0:
                        self.C[sn,n2-1] = -1
                else:
                    if n1 != 0:
                        self.C[n1-1] = 1
                    if n2 != 0:
                        self.C[n2-1] = -1
                sn += 1   #increment source count
            if x == 'E':   # vcvs type, ik column is altered at n1 and n2, cn1 & cn2 get value
                if self.i_unk > 1:  #is B greater than 1 by n?, E
                    if n1 != 0:
                        self.C[sn,n1-1] = 1
                    if n2 != 0:
                        self.C[sn,n2-1] = -1
                    # add entry for cp and cn of the controlling voltage
                    if cn1 != 0:
                        self.C[sn,cn1-1] = -sympify(self.df.loc[i,'element'].lower())
                    if cn2 != 0:
                        self.C[sn,cn2-1] = sympify(self.df.loc[i,'element'].lower())
                else:
                    if n1 != 0:
                        self.C[n1-1] = 1
                    if n2 != 0:
                        self.C[n2-1] = -1
                    vn1, vn2, df2_index = self.__find_vname(self.df.loc[i,'Vname'])
                    if vn1 != 0:
                        self.C[vn1-1] = -sympify(self.df.loc[i,'element'].lower())
                    if vn2 != 0:
                        self.C[vn2-1] = sympify(self.df.loc[i,'element'].lower())
                sn += 1   #increment source count

            if x == 'L':
                if self.i_unk > 1:  #is B greater than 1 by n?, L
                    if n1 != 0:
                        self.C[sn,n1-1] = 1
                    if n2 != 0:
                        self.C[sn,n2-1] = -1
                else:
                    if n1 != 0:
                        self.C[n1-1] = 1
                    if n2 != 0:
                        self.C[n2-1] = -1
                sn += 1   #increment source count

        # check source count
        if sn != self.i_unk:
            print('source number, sn={:d} not equal to self.i_unk={:d} in matrix self.C'.format(sn,self.i_unk))

        #print(self.C)   # display the C matrix
    
    def __D_matrix(self):
        # generate the self.D Matrix
        sn = 0   # count source number as code walks through the data frame
        for i in range(len(self.df)):
            n1 = self.df.loc[i,'p node']
            n2 = self.df.loc[i,'n node']
            #cn1 = self.df.loc[i,'cp node'] # nodes for controlled sources
            #cn2 = self.df.loc[i,'cn node']
            #n_vout = self.df.loc[i,'Vout'] # node connected to op amp output

            # process elements with input to self.D matrix
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if (x == 'V') or (x == 'O') or (x == 'E'):  # need to count V, E & O types
                sn += 1   #increment source count

            if x == 'L':
                if self.i_unk > 1:  #is self.D greater than 1 by 1?
                    self.D[sn,sn] += -s*sympify(self.df.loc[i,'element'])
                else:
                    self.D[sn] += -s*sympify(self.df.loc[i,'element'])
                sn += 1   #increment source count

            if x == 'H':  # H: ccvs
                # if there is a H type, self.D is m by m
                # need to find the vn for Vname
                # then stamp the matrix
                vn1, vn2, df2_index = self.__find_vname(self.df.loc[i,'Vname'])
                self.D[sn,df2_index] += -sympify(self.df.loc[i,'element'].lower())
                sn += 1   #increment source count

            if x == 'F':  # F: cccs
                # if there is a F type, self.D is m by m
                # need to find the vn for Vname
                # then stamp the matrix
                vn1, vn2, df2_index = self.__find_vname(self.df.loc[i,'Vname'])
                self.D[sn,df2_index] += -sympify(self.df.loc[i,'element'].lower())
                self.D[sn,sn] = 1
                sn += 1   #increment source count

            if x == 'K':  # K: coupled inductors, KXX LYY LZZ value
                # if there is a K type, self.D is m by m
                vn1, vn2, ind1_index = self.__find_vname(self.df.loc[i,'Lname1'])  # get i_unk position for Lx
                vn1, vn2, ind2_index = self.__find_vname(self.df.loc[i,'Lname2'])  # get i_unk position for Ly
                # enter sM on diagonals = value*sqrt(LXX*LZZ)

                self.D[ind1_index,ind2_index] += -s*sympify('M{:s}'.format(self.df.loc[i,'element'].lower()[1:]))  # s*Mxx
                self.D[ind2_index,ind1_index] += -s*sympify('M{:s}'.format(self.df.loc[i,'element'].lower()[1:]))  # -s*Mxx

        # display the The self.D matrix
        #print("D: ",self.D)

    def __V_matrix(self):
        # generate the V matrix
        for i in range(self.num_nodes):
            self.V[i] = sympify('v{:d}'.format(i+1))

        #print(self.V)  # display the V matrix

    def __J_matrix(self):
        # The J matrix is an m by 1 matrix, with one entry for each i_unk from a source
        #sn = 0   # count i_unk source number
        #oan = 0   #count op amp number
        for i in range(len(self.df2)):
            # process all the unknown currents
            self.J[i] = sympify('I_{:s}'.format(self.df2.loc[i,'element']))

        #print("J: ", self.J)  # diplay the J matrix

    def __I_matrix(self):
        # generate the I matrix, current sources have n2 = arrow end of the element
        for i in range(len(self.df)):
            n1 = self.df.loc[i,'p node']
            n2 = self.df.loc[i,'n node']
            # process all the passive elements, save conductance to temp value
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if x == 'I':
                g = sympify(self.df.loc[i,'element'])
                # sum the current into each node
                if n1 != 0:
                    self.I[n1-1] -= g
                if n2 != 0:
                    self.I[n2-1] += g

        #print("I: ", self.I)  # display the I matrix

    def __Ev_matrix(self):
        # generate the E matrix
        sn = 0   # count source number
        for i in range(len(self.df)):
            # process all the passive elements
            x = self.df.loc[i,'element'][0]   #get 1st letter of element name
            if x == 'V':
                self.Ev[sn] = sympify(self.df.loc[i,'element'])
                sn += 1

        #print(self.Ev)   # display the E matrix

    def __Z_matrix(self):
        self.Z = self.I[:] + self.Ev[:]  # the + operator in python concatenates the lists
        #print("Z: ", self.Z)  # display the Z matrix

    def __X_matrix(self):
        self.X = self.V[:] + self.J[:]  # the + operator in python concatenates the lists
        #print("X: ", self.X)  # display the X matrix

    def __A_matrix(self):
        n = self.num_nodes
        m = self.i_unk
        self.A = zeros(m+n,m+n)
        for i in range(n):
            for j in range(n):
                self.A[i,j] = self.G[i,j]

        if self.i_unk > 1:
            for i in range(n):
                for j in range(m):
                    self.A[i,n+j] = self.B[i,j]
                    self.A[n+j,i] = self.C[j,i]

            for i in range(m):
                for j in range(m):
                    self.A[n+i,n+j] = self.D[i,j]

        if self.i_unk == 1:
            for i in range(n):
                self.A[i,n] = self.B[i]
                self.A[n,i] = self.C[i]
            self.A[n,n] = self.D[0] # added 1/7/2024 while debugging source free circuit with one inductor

        #print("A: ", self.A)  # display the A matrix

    def numeric_A_matrix(self):
        equ = Eq(self.A*Matrix(self.X),Matrix(self.Z))
        return equ
    
    def components_values(self):
        # print a list of the element values in python dictionary format
        dic = {}
        for i in range(len(self.df)):
            if self.df.iloc[i]['element'][0] == 'F' or self.df.iloc[i]['element'][0] == 'E' or self.df.iloc[i]['element'][0] == 'G' or self.df.iloc[i]['element'][0] == 'H':
                #print('{:s}:{:f},'.format(self.df.iloc[i]['element'].lower(),np.float32(self.df.iloc[i]['value'])))
                dic[sympify(self.df.iloc[i]['element'])]=np.float32(self.df.iloc[i]['value'])
            else:
                #print('{:s}:{:.4e},'.format(self.df.iloc[i]['element'],np.float32(self.df.iloc[i]['value'])))
                dic[sympify(self.df.iloc[i]['element'])]=np.float32(self.df.iloc[i]['value'])
        return dic

    def build(self):
        # initialize variables
        self.num_rlc = 0 # number of passive elements
        self.num_ind = 0 # number of inductors
        self.num_v = 0    # number of independent voltage sources
        self.num_i = 0    # number of independent current sources
        self.i_unk = 0  # number of current unknowns
        self.num_opamps = 0   # number of op amps
        self.num_vcvs = 0     # number of controlled sources of various types
        self.num_vccs = 0
        self.num_cccs = 0
        self.num_ccvs = 0
        self.num_cpld_ind = 0 # number of coupled inductors

        self.__pre_processing()
        self.__parser()
        self.__print_netlist_report()
        self.__init_matrix()
        self.__G_matrix()
        self.__B_matrix()
        self.__C_matrix()
        self.__D_matrix()
        self.__V_matrix()
        self.__J_matrix()
        self.__I_matrix()
        self.__Ev_matrix()
        self.__Z_matrix()
        self.__X_matrix()
        self.__A_matrix()

        return self.A