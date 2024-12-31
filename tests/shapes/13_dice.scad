$fn=8;

pips = [
  [[0, 0]], // 1
  [[1, 1], [-1, -1]], // 2
  [[1, 1], [-1, -1], [0, 0]], // 3
  [[1, 1], [-1, -1], [1, -1], [-1, 1]], // 4
  [[1, 1], [-1, -1], [1, -1], [-1, 1], [0, 0]], // 5
  [[1, 1], [1, -1], [1, 0], [-1, 1], [-1, -1], [-1, 0]], // 6
];

module Face(n) {
  difference() {
    offset(r=10) square([50, 50], center=true);
    difference() {
      square([50, 50], center=true);
      for(loc=pips[n-1])
        translate([12.5*loc[0], 12.5*loc[1]]) circle(d=7);
    }
  }
}


translate([-90,40]) Face(1);
translate([0,40]) Face(2);
translate([90,40]) Face(3);

translate([-90,-40]) Face(4);
translate([0,-40]) Face(5);
translate([90,-40]) Face(6);
