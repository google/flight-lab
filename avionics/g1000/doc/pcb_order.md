# How To Order The Boards

## Chose a PCB Fabricator

Shop around with [PCBShopper](https://pcbshopper.com/) to find the best price
and quality.

## Upload the Gerber Files

Upload the following files one at a time to the PCB fabricator you've chosen:

* bottom/gerber_v3/bottom.zip
* left_side_autopilot/gerber_v3/left_side_auto.zip
* right_side/gerber_v3/right_side.zip

Note: Even if you don't want the GFC-700 autopilot, you should use the
left_side_autopilot files.  Just leave the autopilot buttons, diodes, and OR
gate unpopulated.  The files in left_side use a different kind of tactile
switch that proved very unreliable.

## Specify the PCB Parameters

* Layers: 2
* PCB thickness: 1.6mm
* Gold fingers: No
* Copper weight: 1oz

Note: This design contains internal cutouts.  Not all fabricators support
this.  We've had good results with both JLPCB and OSHPark.

You may want to order a solder stencil to save time.  We haven't done this,
but at times we wish we had.
