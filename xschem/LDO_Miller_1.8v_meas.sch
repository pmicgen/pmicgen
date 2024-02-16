v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1180 -1060 1180 -990 { lab=Vout}
N 1180 -930 1180 -900 { lab=#net1}
N 1180 -840 1180 -780 { lab=0}
N 980 -780 1180 -780 { lab=0}
N 980 -940 980 -780 { lab=0}
N 780 -1060 840 -1060 { lab=Vin}
N 1120 -1060 1280 -1060 { lab=Vout}
C {devices/capa.sym} 1180 -960 0 0 {name=C2
m=1
value=1u
footprint=1206
device="ceramic capacitor"}
C {devices/res.sym} 1180 -870 0 0 {name=R3
value=100m
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 780 -1060 0 0 {name=l1 sig_type=std_logic lab=Vin}
C {devices/lab_pin.sym} 980 -780 0 0 {name=l2 sig_type=std_logic lab=0}
C {devices/lab_pin.sym} 1280 -1060 0 1 {name=l3 sig_type=std_logic lab=Vout}
C {devices/code_shown.sym} 1425 -1605 0 0 {name=NGSPICE1
only_toplevel=true
value=" 
************************************************
*Source initialization
************************************************
VVin Vin 0 DC 0 AC 0
Iout Vout 0 DC 0 AC 0 
************************************************
*Input/Output Characteristic
************************************************
.control
dc VVin 0 2.2 0.2
show
plot Vin Vout
meas DC Vreg WHEN Vout=1.8
print Vreg-1.8
.endc
************************************************
*Line regulation
************************************************
.control
alter Iout DC = 100u
dc VVin 1.8 2.3 0.01
plot Vout
meas DC Vmin FIND Vout AT=1.95
meas DC Vmax FIND Vout AT=2.2
print (Vmax-Vmin)/0.25
.endc
************************************************
*Load regulation and Quiescent current
************************************************
.control
alter VVin DC = 2
dc Iout 0 1m 10u
plot Vout
plot i(VVin)
meas DC Iq FIND i(VVin) AT=0
meas DC Vmax FIND Vout AT=0
meas DC Vmin FIND Vout AT=1m
print (Vmax-Vmin)/1m
.endc
************************************************
*Temerature variation 
************************************************
.control
alter VVin DC = 2 
dc TEMP -45 125 1
plot Vout
meas DC Vout_nom FIND Vout AT=27
meas DC Vout_neg40 FIND Vout AT=-40
meas DC Vout_120 FIND Vout AT=120
.endc
************************************************
*PSRR analysis
************************************************
.control
alter VVin DC = 2
alter VVin AC = 1  
ac dec 10 1 100MEG
plot db(Vout)
meas AC PSR_1k FIND vdb(Vout) AT=1k
meas AC PSR_1M FIND vdb(Vout) AT=1MEG 
.endc
************************************************
*Line Transient
************************************************
.control
alter Iout DC = 100u 
alter @VVin[pulse] = [ 1.95 2.2 50u 5u 5u 50u 100u ]
tran 20u 150u
plot Vin Vout
.endc
************************************************
*Load Transient
************************************************
.control
alter VVin DC = 2 
alter @Iout[pulse] = [ 0 100u 50u 5u 5u 50u 100u ]
tran 20u 150u
plot Iout Vout
.endc
************************************************
*Quiescent current Transient
************************************************
.control
alter VVin DC = 2
alter Iout DC = 0
tran 20u 400u
plot i(VVin) 
.endc
************************************************
.end
" }
C {LDO_Miller_OTA_1.8v.sym} 980 -1060 0 0 {name=x1}
C {devices/code.sym} 1170 -1280 0 0 {name=LIB
format="tcleval( @value )"
value="
.lib /home/designer/.volare/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.include /home/designer/.volare/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_mim_m3_2.model.spice
"}
