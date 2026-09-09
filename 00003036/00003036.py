import cadquery as cq

flange_radius = 0.011
body_radius = 0.00875
bore_radius = 0.0079875
center_bore_radius = 0.006945

half_length = 0.00635
flange_thickness = 0.0016
center_half_length = 0.00155
chamfer_size = 0.0003

shoulder_position = half_length - flange_thickness

profile = [
    (flange_radius, -half_length),
    (flange_radius, -shoulder_position),
    (body_radius, -shoulder_position),
    (body_radius, shoulder_position),
    (flange_radius, shoulder_position),
    (flange_radius, half_length),
    (bore_radius + chamfer_size, half_length),
    (bore_radius, half_length - chamfer_size),
    (bore_radius, center_half_length),
    (center_bore_radius, center_half_length),
    (center_bore_radius, -center_half_length),
    (bore_radius, -center_half_length),
    (bore_radius, -half_length + chamfer_size),
    (bore_radius + chamfer_size, -half_length),
]

solid = (cq.Workplane("XY")
         .polyline(profile).close()
         .revolve(360, (0, 0), (0, 1))
         )

show_object(solid)
