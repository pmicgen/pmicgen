.subckt mabrains_erroramp Vout Vdd GND Vp Vn Ibias
M2 net1 Vn net3 GND nmos_hvt l=500e-9 w=2415e-9 nf=2 m=4
M3 net2 Vp net3 GND nmos_hvt l=500e-9 w=2415e-9 nf=2 m=4
M4 net1 net1 Vdd Vdd pmos_hvt l=500e-9 w=1470e-9 nf=2 m=4
M5 net2 net1 Vdd Vdd pmos_hvt l=500e-9 w=1470e-9 nf=2 m=4
M6 Vout net2 Vdd Vdd pmos_hvt l=500e-9 w=1470e-9 nf=2 m=16
M7 net3 Ibias GND GND nmos_hvt l=500e-9 w=630e-9 nf=1 m=4
M9 Vout Ibias GND GND nmos_hvt l=500e-9 w=630e-9 nf=1 m=64
M1 Ibias Ibias GND GND nmos_hvt l=500e-9 w=630e-9 nf=1 m=4
.ends mabrains_erroramp

