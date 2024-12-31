$fn=32;

difference() {
  square([30,30], center=true);
  difference() {
    union() {
      hull() {
        circle(d=20);
        translate([0, 10]) square([20,1], center=true);
      }
      hull() {
        translate([6.5,-3]) circle(d=6);
        translate([7.5,-7]) circle(d=6);
      }
    }
    hull() {
      translate([1,0]) circle(d=8);
      translate([1, 10]) square([8,2], center=true);
    }
  }
}
