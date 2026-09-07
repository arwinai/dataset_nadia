import cadquery as cq

length_x = 0.0127
length_y = 0.0508
height = 0.0027875
hole_diameter = 0.006

coord_x_center = 0.00635
coord_y_center = 0.0254

hole_offset_x = -0.0000846
hole_offset_y_lower = -0.0154
hole_offset_y_upper = 0.0046

solid = (cq.Workplane("XY")
         .center(coord_x_center, coord_y_center)
         .rect(length_x, length_y)
         .extrude(height)
         .faces(">Z")
         .workplane(centerOption="CenterOfMass")
         .pushPoints([(hole_offset_x, hole_offset_y_lower),
                      (hole_offset_x, hole_offset_y_upper)])
         .hole(hole_diameter)
         )

show_object(solid)
