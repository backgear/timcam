offset(r=1,$fn=256) offset(r=-1) difference() {
    hull() {
        circle(d=20);
        translate([15,0]) circle(d=10);
    }
    circle(d=14);
    translate([-100,-50]) square([100,100]);
}
