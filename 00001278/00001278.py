import cadquery as cq

scale = 0.001

body_left_x = -45.951348
body_right_x = 48.700754
body_top_z = 43.934859
top_fillet_radius = 20.0
bottom_fillet_radius = 5.0

left_lower_control = (-45.788310, 9.240855)
left_upper_control = (-45.625233, 18.481611)
left_shoulder = (-36.680124, 25.539244)
crown_left_control = (-22.436218, 36.777593)
crown_right_control = (14.075723, 42.480333)
right_shoulder = (31.886009, 32.242254)
right_upper_control = (44.825421, 24.804151)
right_lower_control = (47.893691, 8.952137)

bottom_curve_radius = 103.886202
bottom_curve_center_y = 1.395622
bottom_curve_center_z = -98.406026

body_length = body_right_x - body_left_x
body_center_x = (body_left_x + body_right_x) / 2
blank_height = body_top_z - bottom_curve_center_z

body = (
    cq.Workplane("XY", origin=(0, 0, bottom_curve_center_z))
    .moveTo(body_left_x, 0)
    .bezier([left_lower_control, left_upper_control, left_shoulder],
            includeCurrent=True)
    .bezier([crown_left_control, crown_right_control, right_shoulder],
            includeCurrent=True)
    .bezier([right_upper_control, right_lower_control, (body_right_x, 0)],
            includeCurrent=True)
    .mirrorX()
    .extrude(blank_height)
    .faces(">Z").edges().fillet(top_fillet_radius)
)

bottom_cut = (
    cq.Workplane("YZ", origin=(
        body_center_x, bottom_curve_center_y, bottom_curve_center_z
    ))
    .circle(bottom_curve_radius)
    .extrude(body_length, both=True)
)

body = (
    body.cut(bottom_cut)
    .faces("<Z").edges().fillet(bottom_fillet_radius)
)

solid = cq.Workplane("XY").add(body.val().scale(scale))

show_object(solid)
