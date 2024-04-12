.subckt ota1st_lvt_jm OUT VDD VSS Vas Vsrc ibias
M1 Vas IN_M Vsrc VSS nmos_lvt l=500e-9 w=420e-9 nf=2 m=1
M2 OUT IN_P Vsrc VSS nmos_lvt l=500e-9 w=420e-9 nf=2 m=1
M3 Vas Vas VDD VDD pmos_lvt l=800e-9 w=420e-9 nf=2 m=1
M4 OUT Vas VDD VDD pmos_lvt l=800e-9 w=420e-9 nf=2 m=1
M7 Vsrc ibias VSS VSS nmos_lvt l=1e-6 w=210e-9 nf=2 m=1
M8 ibias ibias VSS VSS nmos_lvt l=1e-6 w=210e-9 nf=2 m=1
.end ota1st_lvt_jm
