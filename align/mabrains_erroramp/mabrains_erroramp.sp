.subckt mabrains_erroramp Vout Vdd GND Vp Vn Ibias
M2 net1 Vn net3 GND nmos_hvt w=2100e-9 l=210e-9 nf=2 m=2
M3 net2 Vp net3 GND nmos_hvt w=2100e-9 l=210e-9 nf=2 m=2
M4 net1 net1 Vdd Vdd pmos_hvt w=2100e-9 l=210e-9 nf=2 m=2
M5 net2 net1 Vdd Vdd pmos_hvt w=2100e-9 l=210e-9 nf=2 m=2
M6 Vout net2 Vdd Vdd pmos_hvt w=1260e-9 l=210e-9 nf=2 m=8
M7 net3 Ibias GND GND nmos_hvt w=630e-9 l=420e-9 nf=2 m=2
M9 Vout Ibias GND GND nmos_hvt w=630e-9 l=420e-9 nf=2 m=32
M1 Ibias Ibias GND GND nmos_hvt w=630e-9 l=420e-9 nf=2 m=2
.ends mabrains_erroramp