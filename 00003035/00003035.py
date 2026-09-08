import cadquery as cq

plate_length = 0.067
plate_width = 0.0395
plate_thickness = 0.003
corner_radius = 0.005
hole_diameter = 0.0051

hole_centers = [
    (0.007, 0.01975),
    (0.03879, 0.00975),
    (0.03879, 0.01975),
    (0.03879, 0.02975),
    (0.05879, 0.00975),
    (0.05879, 0.01975),
    (0.05879, 0.02975),
]

solid = (cq.Workplane("XY")
         .box(plate_length, plate_width, plate_thickness,
              centered=(False, False, False))
         .edges("|Z")
         .fillet(corner_radius)
         .faces(">Z")
         .workplane(centerOption="ProjectedOrigin")
         .pushPoints(hole_centers)
         .hole(hole_diameter)
         )

show_object(solid)
