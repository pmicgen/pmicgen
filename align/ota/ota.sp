.subckt erroramp Vout Vdd GND Vp Vn Ibias
XM2 net1 Vn net3 GND nmos_hvt l=0.5 w=5 nf=1 m=4
XM3 net2 Vp net3 GND nmos_hvt l=0.5 w=5 nf=1 m=4
XM4 net1 net1 Vdd Vdd pmos_hvt l=0.5 w=3 nf=1 m=4
XM5 net2 net1 Vdd Vdd pmos_hvt l=0.5 w=3 nf=1 m=4
XM6 Vout net2 Vdd Vdd pmos_hvt l=0.5 w=3 nf=1 m=16
XM7 net3 Ibias GND GND nmos_hvt l=0.5 w=0.75 nf=1 m=4
XM9 Vout Ibias GND GND nmos_hvt l=0.5 w=0.75 nf=1 m=64
XM1 Ibias Ibias GND GND nmos_hvt l=0.5 w=0.75 nf=1 m=4
XC1 net2 Vout sky130_fd_pr__cap_mim_m3_1 w=20 l=25 m=1
.ends erroramp