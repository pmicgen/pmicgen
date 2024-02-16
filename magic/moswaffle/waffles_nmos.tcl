
# #####################	#
#   AC3E - UTFSM      	#
#   Project: 3LFCC    	#
#   Un-flatten Waffles	#
#   11-11-2022        	#
# #####################	#


####### NMOS #######

set size 5.5
set n 36
set base 0
set offset_lt 15.25
set offset -1.13
set offset_b -15.75
set guard_width 48
set guard_offset_x 11.25
set guard_offset_y 11.750
set top_offset 5.75
set diff_offset 4
set con_offset 4.12
set dnwell_offset 24.5
set m2_off_x 50.18
set m2_off_y 26.920
set m_track 34
set m_track_width 10
set totop [expr {int(($n-2)*$size*200)}]
set totop_off [expr {$totop+140}]
set totop_hvn [expr {$totop+979}]
set totop_hvn_off [expr {$totop+1007}]
set toright_hvn [expr {$totop+121}]
set toright_hvn_off [expr {$totop+1107}]
set totop_hvn_bot [expr {$totop+21}]
set toright_hvn_bot [expr {$totop+1079}]
set totop2 [expr {$totop+30}]
set totop2_off [expr {$totop+170}]

### corners ###
load nmos_waffle_corners.mag

zoom 8

## take both right and move ##
box [expr {0.000}]um [expr {-15.750}]um [expr {15.750}]um [expr {11.250}]um
select a
move e [expr {($n - 2)*$size}]um
## take top right and move ##
box [expr {($n - 2)*$size}]um [expr { 0.000}]um [expr {($n - 1)*$size+15.750}]um [expr {11.250}]um
select a
move n [expr {($n - 2)*$size}]um
## take top left and move ##
box [expr {-15.250}]um [expr { 0.000}]um [expr {0.000}]um [expr {15.250}]um
select a
move n [expr {($n - 2)*$size}]um

## bottom right corner diff ##
box [expr {($n - 2)*$size - 0.03}]um [expr { -5.19}]um [expr {($n - 2)*$size}]um [expr {-0.810}]um
paint mvndiff
box [expr {($n - 2)*$size + 0.81}]um [expr { 0}]um [expr {($n - 2)*$size+ 5.19}]um [expr {0.03}]um
paint mvndiff
## bottom left corner diff ##
box [expr { -4.69}]um [expr {0}]um [expr {-0.31}]um [expr {0.03}]um
paint mvndiff
## top right corner ##
box [expr {($n - 2)*$size - 0.03}]um [expr { ($n - 2)*$size} + 0.310]um [expr {($n - 2)*$size}]um [expr {($n - 2)*$size +4.69}]um
paint mvndiff

### inside ###

for {set i 0} {$i < $n - 2} {incr i} { #ancho
    for {set j 0} {$j < $n - 2} {incr j} { #alto
		box [expr {$base + $size*$i + $offset}]um [expr {$base + $size*$j + $offset}]um [expr {$base + $size*($i+1) + $offset}]um [expr {$base + $size*($j+1) + $offset}]um
		if {[expr {($i + $j)%2}]} {
			getcell nmos_drain_in.mag
		} else {
			getcell nmos_source_in.mag
		}
	}
}


### frame ###

for {set i 0} {$i < ($n - 2)} {incr i} { #alto
	
	if {[expr {($i)%2}]} {
			### left ###
			box [expr {$base - $offset_lt}]um [expr {$base + $size*$i + $offset}]um [expr {$base + $size - $offset_lt}]um [expr {$base + $size*($i+1) + $offset}]um
			getcell nmos_source_frame_lt.mag
			### right ###
			box [expr {$base + $offset + $size*($n - 2)}]um [expr {$base + $size*$i + $offset}]um [expr {$base + $size*($n-1) + $offset}]um [expr {$base + $size*($i+1) + $offset}]um
			getcell nmos_drain_frame_rb.mag
			### bottom ###
			box [expr {$base + $size*$i + $offset}]um [expr {$base + $offset_b}]um [expr {$base + $size*($i+1) + $offset}]um [expr {$base + $size + $offset_b}]um
			getcell nmos_source_frame_rb.mag
			upsidedown
			clockwise 90
			### top ###
			box [expr {$base + $size*$i + $offset}]um [expr {$base + $size*($n -2) +$offset}]um [expr {$base + $size*($i+1) + $offset}]um [expr {$base + $size*($n-1)}]um
			getcell nmos_drain_frame_lt.mag
			sideways
			clockwise -90
		} else {
			### left ###
			box [expr {$base - $offset_lt}]um [expr {$base + $size*$i + $offset}]um [expr {$base + $size - $offset_lt}]um [expr {$base + $size*($i+1) + $offset}]um
			getcell nmos_drain_frame_lt.mag
			### right ###
			box [expr {$base + $offset + $size*($n - 2)}]um [expr {$base + $size*$i + $offset}]um [expr {$base + $size*($n-1) + $offset}]um [expr {$base + $size*($i+1) + $offset}]um
			getcell nmos_source_frame_rb.mag
			### bottom ###
			box [expr {$base + $size*$i + $offset}]um [expr {$base + $offset_b}]um [expr {$base + $size*($i+1)} + $offset]um [expr {$base + $size + $offset_b}]um
			getcell nmos_drain_frame_rb.mag
			upsidedown
			clockwise 90		
			### top ###
			box [expr {$base + $size*$i + $offset}]um [expr {$base + $size*($n -2) +$offset}]um [expr {$base + $size*($i+1) + $offset }]um [expr {$base + $size*($n-1)}]um
			getcell nmos_source_frame_lt.mag
			sideways
			clockwise -90
		}
}


### guard ring (exterior) ###

## bottom ##
box [expr {-$guard_offset_x - $guard_width}]um [expr {-$guard_offset_y - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width}]um [expr {-$guard_offset_y }]um
paint nwell
#box [expr {-$guard_offset_x + $dnwell_offset - $guard_width}]um [expr {-$guard_offset_y + $dnwell_offset - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width - $dnwell_offset}]um [expr {-$guard_offset_y }]um
#paint dnwell
box [expr {-$guard_offset_x + $diff_offset - $guard_width}]um [expr {-$guard_offset_y + $diff_offset - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5  - $diff_offset + $guard_width}]um [expr {-$guard_offset_y- $diff_offset}]um
paint metal1
paint mvnsubstratendiff
paint locali
box [expr {-$guard_offset_x + $diff_offset - $guard_width + $m2_off_x}]um [expr {-$guard_offset_y + $diff_offset - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5  - $diff_offset + $guard_width}]um [expr {-$guard_offset_y - $diff_offset}]um
paint metal2
box [expr {-$guard_offset_x + $con_offset - $guard_width}]um [expr {-$guard_offset_y + $con_offset - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5 - $con_offset + $guard_width}]um [expr {-$guard_offset_y - $con_offset}]um
paint viali
paint mvnsubstratencontact
box [expr {-$guard_offset_x + $con_offset - $guard_width + $m2_off_x}]um [expr {-$guard_offset_y + $con_offset - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5 - $con_offset + $guard_width}]um [expr {-$guard_offset_y - $con_offset}]um
paint m2contact
# metal track #
box [expr {-$guard_offset_x - $guard_width + $m_track + 20}]um [expr {-$guard_offset_y - $guard_width + $m_track}]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width - $m_track}]um [expr {-$guard_offset_y - 4}]um
paint metal3
paint metal4
paint metal5

## top ##
box [expr {-$guard_offset_x - $guard_width}]um [expr {($n-1)*$size + $top_offset}]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width}]um [expr {($n-1)*$size + $top_offset + $guard_width}]um
paint nwell
#box [expr {-$guard_offset_x + $dnwell_offset - $guard_width}]um [expr {($n-1)*$size + $top_offset}]um [expr {($n-1)*$size + $guard_offset_x - 5  + $guard_width - $dnwell_offset}]um [expr {($n-1)*$size + $top_offset - $dnwell_offset + $guard_width}]um
#paint dnwell
box [expr {-$guard_offset_x + $diff_offset - $guard_width}]um [expr {($n-1)*$size + $top_offset + $diff_offset }]um [expr {($n-1)*$size + $guard_offset_x - 5 - $diff_offset + $guard_width}]um [expr {($n-1)*$size + $top_offset + $guard_width - $diff_offset}]um
paint metal1
paint mvnsubstratendiff
paint locali
paint metal2
box [expr {-$guard_offset_x + $con_offset - $guard_width}]um [expr {($n-1)*$size + $top_offset + $con_offset }]um [expr {($n-1)*$size + $guard_offset_x - 5  - $con_offset + $guard_width}]um [expr {($n-1)*$size + $top_offset  + $guard_width - $con_offset}]um
paint viali
paint mvnsubstratencontact
paint m2contact
# metal track #
box [expr {-$guard_offset_x - $guard_width + $m_track}]um [expr {($n-1)*$size + $top_offset + 4}]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width - $m_track - 20}]um [expr {($n-1)*$size + $top_offset + $m_track_width + 4}]um
paint metal3
paint metal4
paint metal5

## left ##
box [expr {-$guard_offset_x - $guard_width}]um [expr {-$guard_offset_y}]um [expr {-$guard_offset_x}]um [expr {($n-1)*$size +$top_offset}]um
paint nwell
#box [expr {-$guard_offset_x + $dnwell_offset - $guard_width}]um [expr {-$guard_offset_y}]um [expr {-$guard_offset_x}]um [expr {($n-1)*$size + $top_offset}]um
#paint dnwell
box [expr {-$guard_offset_x + $diff_offset - $guard_width}]um [expr {-$guard_offset_y - $diff_offset }]um [expr {-$guard_offset_x - $diff_offset}]um [expr {($n-1)*$size + $top_offset  + $diff_offset}]um
paint metal1
paint mvnsubstratendiff
paint locali
box [expr {-$guard_offset_x + $diff_offset - $guard_width}]um [expr {-$guard_offset_y - $diff_offset + $m2_off_y}]um [expr {-$guard_offset_x - $diff_offset}]um [expr {($n-1)*$size + $top_offset  + $diff_offset}]um
paint metal2
box [expr {-$guard_offset_x + $con_offset - $guard_width}]um [expr {-$guard_offset_y - $con_offset }]um [expr {-$guard_offset_x - $con_offset}]um [expr {($n-1)*$size + $top_offset  + $con_offset}]um
paint viali
paint mvnsubstratencontact
box [expr {-$guard_offset_x + $con_offset - $guard_width}]um [expr {-$guard_offset_y - $diff_offset + $m2_off_y}]um [expr {-$guard_offset_x - $con_offset}]um [expr {($n-1)*$size + $top_offset + $diff_offset}]um
paint m2contact
# metal track #
box [expr {-$guard_offset_x - $guard_width + $m_track}]um [expr {-$guard_offset_y + 6}]um [expr {-$guard_offset_x - $guard_width + $m_track + $m_track_width}]um [expr {($n-1)*$size + $top_offset + 4}]um
paint metal3
paint metal4 
paint metal5

## right ##
box [expr {($n-1)*$size + $guard_offset_x - 5}]um [expr {-$guard_offset_y}]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width}]um [expr {($n-1)*$size + $top_offset}]um
paint nwell
#box [expr {($n-1)*$size + $guard_offset_x - 5}]um [expr {-$guard_offset_y}]um [expr {($n-1)*$size + $guard_offset_x - 5 - $dnwell_offset + $guard_width}]um [expr {($n-1)*$size + $top_offset}]um
#paint dnwell
box [expr {($n-1)*$size + $guard_offset_x - 5 + $diff_offset}]um [expr {-$guard_offset_y - $diff_offset }]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width - $diff_offset}]um [expr {($n-1)*$size + $top_offset  + $diff_offset}]um
paint metal1
paint mvnsubstratendiff
paint locali
paint metal2
box [expr {($n-1)*$size + $guard_offset_x - 5 + $con_offset}]um [expr {-$guard_offset_y - $con_offset }]um [expr {($n-1)*$size + $guard_offset_x - 5 + $guard_width - $con_offset}]um [expr {($n-1)*$size + $top_offset  + $con_offset}]um
paint viali
paint mvnsubstratencontact
paint m2contact
# metal track #
box [expr {($n-1)*$size + $guard_offset_x - 1}]um [expr {-$guard_offset_y - 4}]um [expr {($n-1)*$size + $guard_offset_x + $m_track_width - 1}]um [expr {($n-1)*$size + $top_offset - 6}]um
paint metal3
paint metal4 
paint metal5

# dnwell #

box [expr {-$guard_offset_x + $dnwell_offset - $guard_width}]um [expr {-$guard_offset_y + $dnwell_offset - $guard_width}]um [expr {($n-1)*$size + $guard_offset_x - 5  + $guard_width - $dnwell_offset}]um [expr {($n-1)*$size + $top_offset - $dnwell_offset + $guard_width}]um
paint dnwell

save nmos_36x36

# topleft corner,  botleft corner, topright corner, botright corner
# -140 $totop 0 $totop_off -140 $totopsize_off 0 $totopsize -1100 $totop -960 $totop_off -1100 $totopsize_off -960 $totopsize || topleft
# -140 -140 0 0 -$hintsize -140 -$hintsize_off 0 -$hintsize -$hintheight -$hintsize_off -$hintheight_off -140 -$hintheight 0 -$hintheight_off || botleft
# $totop -140 $totop_off 0 $totop -$hintheight $totop_off -$hintheight_off $totopsizere -140 $totopsizere_off 0 $totopsizere -$hintheight $totopsizere_off -$hintheight_off || botright
# $totop $totop $totop_off $totop_off $totopsizere_off $totop $totopsizere $totop_off $totop $totopsize_off $totop_off $totopsize $totopsizere_off $totopsize_off $totopsizere $totopsize || botleft
property MASKHINTS_HVI "-140 $totop 0 $totop_off -140 -140 0 0 $totop -140 $totop_off 0 $totop $totop $totop_off $totop_off"
property MASKHINTS_HVNTM "-1007 -1107 -21 -1079 -1007 -1079 -979 -121 $toright_hvn $totop_hvn $toright_hvn_off $totop_hvn_off $toright_hvn_bot $totop_hvn_bot $toright_hvn_off $totop_hvn -170 $totop2 -30 $totop2_off"
save