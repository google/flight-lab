# Parts Fabrication

## Front Panel

There are a couple of options for fabricating the front panel.

### Using a multi-material 3d printer (preferrably SLA)

Pros:

* High quality result.
* Supports backlighting.
* Minimal post-processing.

Cons:

* Requires expensive equipment.

This approach requires a multi-material printer with very fine resolution.  The
printer will be creating small font text on the face plate, so precision is
essential.  These steps have been tested on an Objet500.

#### Print the parts

Print the following parts using the colors specified.  Look in models/v2_release
for the STL files.

* g1000_composite - g1000_clear-1.STL: 50/50 Clear and White

These two parts should be printed together.  Ensure that they share a common
origin.

* g1000_composite - g1000-1.STL: Black
* g1000_composite - g1000_ text_new-1.STL: White

The bulk of the frame is a 50/50 mix of clear and white.  This gives a good
compromise between light diffusion and transmission.

#### Finish the parts

* Use plastic scrapers and brushes under running water to remove the support
  material.
* Sand the front panel with 220 and then 400 grit sandpaper.
* Apply spray on clear coat.

#### Apply shielding

The one drawback of this approach is that the black frame is partially
translucent.  This means we need something to fully block the light in the
non-text areas.

We have had ok results using a layer of aluminum foil between the front panel
and the clear core.  The aluminum is cut to fit in the recess with an exacto
knife.  Then cutouts are added everywhere there is text or graphics.  This
blocks the light very well, but it is difficult to avoid tearing the foil.

In the future we may experiment with stencils and black spray paint or laser
cut paper shields.

### Using a desktop FDM 3D printer

Pros:

* Cheap
* May support backlighting

Cons:

* Labor intensive
* Experimental.

#### Print the parts

Print the following parts.  Look in models/v2_release for the STL files.

* left_side.STL
* right_side.STL

If you plan to use backlighting, these parts must be clear.  It is also
recommended that you use a high strength plastic with low warping such as
PETG.

#### Sanding and assembly

Sand until your hands ache.  It may also be worthwhile to use an expoxy filler
such as XTC-3D.  Then assemble the two halves using m3 square nuts and m3x25
hex socket cap screws.

#### Text options

* Print the text on a transparency sheet and glue the transparency to the frame.
  Then mask off the transparency and spray paint the rest of the frame black.
  Untested.
* Print the text on label paper and apply the labels to the frame.  Mask off the
  labels and spray paint the rest of the frame black.  Apply a layer of clear
  coat to seal the label to the frame.  This method is NOT compatible with
  backlighting.  Optional: Better results can be achieved by applying MANY
  layers of Mod Podge on top of the label before adding clear coat.  Eventually
  the label is encased in the Mod Podge and looks like it is part of the plastic
  frame.  Finish with clear coat.

## Buttons

### Using a multi-material 3d printer (preferrably SLA)

See the instructions for the face plate for more detail.  Each button should
be printed using the colors specified.  Look in models/v2_release
for the STL files.  Each button is made of three parts that must be printed
with a common origin.

* button_$NAME - button_base-1.STL: 50/50 clear and white
* button_$NAME - button_cap_$NAME-1.STL: Black
* button_$NAME - Part#^button_$NAME-1.STL: White

Here are the quantities needed:

* button_arrow: 12
* button_transfer: 2
* All other buttons: 1 each

### Using a desktop FDM 3D printer

In theory this could be done in the same manner as the frame.  However, doing
so would require an enormous amount of tedious labor.  This has not been
attempted.

## Monitor support

3D Print models/v2_release/screen_mount.STL.  Use whatever method is convenient.
If using an FDM printer, you'll need to generate supports in your slicer.

## Assembly

* Nest the clear frame core into the black face plate. Be sure to include
  the foil or paper light filter.
* If using backlighting, insert LED strip lighting into the channel around the
  edge with the LEDs facing inward.
* Insert all the buttons into their holes.
* Insert the three PCBs into their slots.  Attach with #6-32 screws.
* Attach the encoders to the frame with the nuts that came with them.
* Attach the monitor control boards to the monitor support with #6-32 and
  #4-40 screws.
* Lay the monitor on top of the back of the frame.  Lay the monitor support
  on top of it, aligning with the holes in the frame.
* Route the cables from the monitor control board to the monitor through the
  monitor support.
* Attach the monitor support to the frame with #6-32 screws.  Use caution around
  the ribbon cable on the right side.  It can bind against the monitor support
  and become damaged.
* The G1000 is complete!  Plug in the HDMI, power, and USB cables and test!
* Install into the instrument panel with #6-32 screws.
