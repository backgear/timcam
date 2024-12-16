$fn=16;

for(r=[0,180])
rotate([0,0,r])
for(t=[0:0.1:100])
    hull() {
        dot(t);
        dot(t+0.1);
    }

module dot(n) {
    rotate([0,0,n*17]) translate([8+n,0,0]) circle(d=6);
}
