# timcam

Makefile-friendly cross-platform CAM.

# Goals

* Feature parity with cammill's batch mode
* Circular trochoidal pocket milling
* G2/G3 arc reconstruction
* Linking by small arcs

# Stretch goals

* Interactive GUI to preview step tree
* Interactive GUI to set tool params
* Stock removal simulation
    * Graph of MRR, chipload
    * Graph of conventional/climb/slot effective cutting
    * Corner optimization (either feedrate reduction, or stepover reduction)
    * Force vector calculation (flute helix, non-center-cutting endmill, plus
      deflection forces)

# Rough design

* `Status` base class suitable for CLI or GUI kicks things off and reads config
* `Step` base class with a lightweight `__init__` and the actual work done in a
  `run` method (to be done in threads, in parallel).
* `Step`s report their progress to the `Status` (right now this just logs, but
  could be used for a progress bar later)
* Dotted keys let you relate one phase step to the next one(s), e.g. `0` might
  be to load a dxf, and `0.0` might be shape identification, and `0.0.0` and
  `0.0.1` might be profile and pocket milling.
* Each phase is responsible for queueing the next phase's steps in the `Status.executor`
* Entry point `python -m timcam.api /path/to/dxf` (will save Chrome Trace in
  `trace.out` and various step images in `preview/` subdir).

## Phase design braindump

* tc0 (lines)
    * loader
    * fixups (some arc reconstruction, dejumble, etc)
    * result: barely-structured/sorted Loop objects
* tc1 (shapes)
    * intent (inside/outside/mill/drill)
    * depth/operation "layers" (becomes first component of name)
    * tool selection
    * roughing/finishing
    * stock to leave
    * result: PolyIntent [with islands]/CircleIntent (becomes second component
      of name), potentially doubling number of objects
* tc2 (plan)
    * voronoi
    * machine-generated path arcs (becomes third component of name)
    * climb vs conventional
* tc3 (optimization)
    * linking
    * aircutting removal
    * excessive engagement reduction (tell tc2 to reduce stepover for some arcs)
    * final arc reconstruction
* tc4 (g-code output, serial?)
