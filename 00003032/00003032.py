import cadquery as cq

length = 0.533402026
bore_radius = 0.0021
bore_spacing = 0.02
half_width = 0.01

web_half_width = 0.0039
notch_half_width = 0.0001
notch_depth = 0.0001
core_chamfer_x = 0.002840365
core_shoulder_x = 0.00624
core_shoulder_top_z = -0.007299635
wall_inner_x = 0.0082

top_slot_wall_x = 0.0055
top_slot_mouth_x = 0.00289
top_slot_diagonal_z = 0.016558826
top_slot_lip_z = 0.018197506
top_slot_mouth_z = 0.018307505
top_edge_z = 0.019997506
corner_tangent_x = 0.0085

top_lip_arc_start = (0.004348614, 0.01976612)
top_lip_arc_mid = (0.004604909, 0.01993737)
top_lip_arc_end = (0.004907229, top_edge_z)
corner_arc_mid = (0.00956066, 0.019558165)
corner_arc_end = (half_width, 0.018497505)
upper_side_arc_start = (half_width, 0.014904734)
upper_side_arc_mid = (0.009939865, 0.014602415)
upper_side_arc_end = (0.009768615, 0.01434612)
lower_side_arc_start = (0.009765686, 0.005654315)
lower_side_arc_mid = (0.009939103, 0.005394776)
lower_side_arc_end = (half_width, 0.005088629)

side_mouth_x = 0.00831
side_shoulder_x = 0.00656
upper_side_mouth_z = 0.012887506
upper_side_lip_z = 0.015497506
upper_side_diagonal_z = 0.012838315
lower_side_diagonal_z = 0.00716
lower_side_lip_z = 0.0045
lower_side_mouth_z = 0.00711

pocket_inner_x = 0.00657
pocket_chamfer_x = 0.00766
pocket_bottom_z = 0.006567506
pocket_chamfer_z = 0.007657506

half_bore_spacing = bore_spacing / 2
section_center_z = -half_bore_spacing
notch_tip_x = web_half_width - notch_depth
core_top_z = -web_half_width
core_bottom_z = -bore_spacing - core_top_z
core_shoulder_bottom_z = -bore_spacing - core_shoulder_top_z
pocket_top_z = top_slot_lip_z - half_bore_spacing

core_hole = [
    (-core_chamfer_x, core_top_z),
    (-notch_half_width, core_top_z),
    (0, core_top_z + notch_depth),
    (notch_half_width, core_top_z),
    (core_chamfer_x, core_top_z),
    (core_shoulder_x, core_shoulder_top_z),
    (wall_inner_x, core_shoulder_top_z),
    (wall_inner_x, core_shoulder_bottom_z),
    (core_shoulder_x, core_shoulder_bottom_z),
    (core_chamfer_x, core_bottom_z),
    (notch_half_width, core_bottom_z),
    (0, core_bottom_z - notch_depth),
    (-notch_half_width, core_bottom_z),
    (-core_chamfer_x, core_bottom_z),
    (-core_shoulder_x, core_shoulder_bottom_z),
    (-wall_inner_x, core_shoulder_bottom_z),
    (-wall_inner_x, core_shoulder_top_z),
    (-core_shoulder_x, core_shoulder_top_z),
]

corner_pocket = [
    (pocket_inner_x, pocket_chamfer_z),
    (pocket_inner_x, pocket_top_z),
    (wall_inner_x, pocket_top_z),
    (wall_inner_x, pocket_bottom_z),
    (pocket_chamfer_x, pocket_bottom_z),
]

bar = (cq.Workplane("XZ", origin=(0, 0, section_center_z))
       .moveTo(0, half_bore_spacing + notch_tip_x)
       .lineTo(notch_half_width, half_bore_spacing + web_half_width)
       .lineTo(core_chamfer_x, half_bore_spacing + web_half_width)
       .lineTo(top_slot_wall_x, top_slot_diagonal_z)
       .lineTo(top_slot_wall_x, top_slot_lip_z)
       .lineTo(top_slot_mouth_x, top_slot_lip_z)
       .lineTo(top_slot_mouth_x, top_slot_mouth_z)
       .lineTo(*top_lip_arc_start)
       .threePointArc(top_lip_arc_mid, top_lip_arc_end)
       .lineTo(corner_tangent_x, top_edge_z)
       .threePointArc(corner_arc_mid, corner_arc_end)
       .lineTo(*upper_side_arc_start)
       .threePointArc(upper_side_arc_mid, upper_side_arc_end)
       .lineTo(side_mouth_x, upper_side_mouth_z)
       .lineTo(wall_inner_x, upper_side_mouth_z)
       .lineTo(wall_inner_x, upper_side_lip_z)
       .lineTo(side_shoulder_x, upper_side_lip_z)
       .lineTo(web_half_width, upper_side_diagonal_z)
       .lineTo(web_half_width, half_bore_spacing + notch_half_width)
       .lineTo(notch_tip_x, half_bore_spacing)
       .lineTo(web_half_width, half_bore_spacing - notch_half_width)
       .lineTo(web_half_width, lower_side_diagonal_z)
       .lineTo(side_shoulder_x, lower_side_lip_z)
       .lineTo(wall_inner_x, lower_side_lip_z)
       .lineTo(wall_inner_x, lower_side_mouth_z)
       .lineTo(side_mouth_x, lower_side_mouth_z)
       .lineTo(*lower_side_arc_start)
       .threePointArc(lower_side_arc_mid, lower_side_arc_end)
       .lineTo(half_width, 0)
       .mirrorX()
       .mirrorY()
       .extrude(-length)
       )

holes = (cq.Workplane("XZ")
         .pushPoints([(0, 0), (0, -bore_spacing)])
         .circle(bore_radius)
         .polyline(core_hole).close()
         )

for x_sign in (-1, 1):
    for z_sign in (-1, 1):
        pocket = [(x_sign * x,
                   z_sign * (z - section_center_z) + section_center_z)
                  for x, z in corner_pocket]
        holes = holes.polyline(pocket).close()

solid = bar.cut(holes.extrude(-length))

show_object(solid)
