%.dxf: %.scad
	openscad -o $@ $<

.PHONY: all
all: $(patsubst %.scad,%.dxf,$(shell ls *.scad))
