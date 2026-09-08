import cadquery as cq

plate_length = 0.082
plate_width = 0.0395
plate_thickness = 0.003
corner_radius = 0.00338

large_hole_radius = 0.0125
large_hole_center = (0.02125, 0.01975)

small_hole_radius = 0.00255
small_hole_centers = [
    (0.0538, 0.00975),
    (0.0538, 0.01975),
    (0.0538, 0.02975),
    (0.0738, 0.00975),
    (0.0738, 0.01975),
    (0.0738, 0.02975),
]

slot_width = 0.00155
slot_center_spacing = 0.0025 * 2 ** 0.5
slot_length = slot_center_spacing + slot_width
slot_positions = [
    (0.007, 0.0055, 45),
    (0.007, 0.034, -45),
    (0.0355, 0.0055, -45),
    (0.0355, 0.034, 45),
]

plate = (cq.Workplane("XY")
         .box(plate_length, plate_width, plate_thickness,
              centered=(False, False, False))
         .edges("|Z")
         .fillet(corner_radius)
         )

large_hole = (cq.Workplane("XY")
              .moveTo(*large_hole_center)
              .circle(large_hole_radius)
              .extrude(plate_thickness)
              )

small_holes = (cq.Workplane("XY")
               .pushPoints(small_hole_centers)
               .circle(small_hole_radius)
               .extrude(plate_thickness)
               )

solid = (plate
         .cut(large_hole)
         .cut(small_holes)
         )

for slot_x, slot_y, slot_angle in slot_positions:
    slot = (cq.Workplane("XY")
            .moveTo(slot_x, slot_y)
            .slot2D(slot_length, slot_width, slot_angle)
            .extrude(plate_thickness)
            )
    solid = solid.cut(slot)

show_object(cq.Compound.makeCompound(solid))
