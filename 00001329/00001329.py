import math
import cadquery as cq

board_thickness = 38.1
scale = 0.001

table_length = 1524.0
table_depth = 457.2
table_height = 762.0
table_center_x = 3.314018
table_center_y = -101.007603

tabletop = (
    cq.Workplane("XY")
    .box(table_length, table_depth, board_thickness, centered=(True, True, False))
    .translate((table_center_x, table_center_y, 0))
)

frame_angle = 22.21412563
rail_length = 330.2
left_frame_inset = 62.705493
right_frame_inset = 52.700559

frame_height = table_height - board_thickness
frame_angle_radians = math.radians(frame_angle)
diagonal_slope = math.tan(frame_angle_radians)
diagonal_projected_width = board_thickness / math.cos(frame_angle_radians)

upper_front_y = table_center_y + rail_length / 2
upper_back_y = upper_front_y - rail_length
upper_bottom_z = -board_thickness
foot_bottom_z = -frame_height
foot_top_z = foot_bottom_z + board_thickness

foot_back_y = (
    upper_front_y + foot_bottom_z * diagonal_slope - diagonal_projected_width
)
foot_front_y = foot_back_y + rail_length
diagonal_top_back_y = (
    upper_front_y + upper_bottom_z * diagonal_slope - diagonal_projected_width
)
diagonal_bottom_front_y = upper_front_y + foot_top_z * diagonal_slope

frame = (
    cq.Workplane("YZ")
    .polyline([
        (upper_back_y, 0),
        (upper_front_y, 0),
        (diagonal_bottom_front_y, foot_top_z),
        (foot_front_y, foot_top_z),
        (foot_front_y, foot_bottom_z),
        (foot_back_y, foot_bottom_z),
        (diagonal_top_back_y, upper_bottom_z),
        (upper_back_y, upper_bottom_z),
    ])
    .close()
    .extrude(board_thickness)
)

left_frame_x = table_center_x - table_length / 2 + left_frame_inset
right_frame_x = (
    table_center_x + table_length / 2 - right_frame_inset - board_thickness
)

left_frame = frame.translate((left_frame_x, 0, 0))
right_frame = frame.translate((right_frame_x, 0, 0))

extension_x = right_frame_x + board_thickness
extension_front_bottom_y = upper_front_y + upper_bottom_z * diagonal_slope

right_top_extension = (
    cq.Workplane("YZ", origin=(extension_x, 0, 0))
    .polyline([
        (upper_back_y, 0),
        (upper_front_y, 0),
        (extension_front_bottom_y, upper_bottom_z),
        (upper_back_y, upper_bottom_z),
    ])
    .close()
    .extrude(board_thickness)
)

solid = cq.Compound.makeCompound([
    tabletop.val(), left_frame.val(), right_frame.val(), right_top_extension.val()
])
solid = cq.Workplane("XY").add(solid.scale(scale))

show_object(solid)
