import math
import cadquery as cq

def round_edges(part, radius, *positions):
    selection = cq.selectors.NearestToPointSelector(positions[0])
    for position in positions[1:]:
        selection += cq.selectors.NearestToPointSelector(position)
    return part.edges(selection).fillet(radius)

scale = 0.001
plate_width = 63.5
plate_height = 63.5
plate_thickness = 6.35
shoulder_height = plate_height / 2
foot_inset = 9.525
notch_left = 25.4
notch_right = 50.8
notch_depth = plate_thickness
hole_radius = 2.0828
clearance_radius = 2.2479
mounting_height = 17.399
mounting_pitch = 14.478
mounting_holes = [
    (plate_thickness, -mounting_height),
    (notch_left, -mounting_height + mounting_pitch / 2),
    (notch_left, -mounting_height - mounting_pitch / 2),
]
alignment_holes = [
    (2 * plate_thickness, -mounting_height),
    (plate_width - plate_thickness, -mounting_height),
]
lower_hole_left = 27.94
lower_hole_pitch = 12.7
lower_hole_top = 38.1
lower_hole_spacing = 19.05
lower_holes = [
    (x, -z)
    for x in (lower_hole_left, lower_hole_left + lower_hole_pitch)
    for z in (lower_hole_top, lower_hole_top + lower_hole_spacing)
]
plate_outline = [
    (0, 0), (notch_left, 0), (notch_left, -notch_depth),
    (notch_right, -notch_depth), (notch_right, 0), (plate_width, 0),
    (plate_width, -shoulder_height), (plate_width - foot_inset, -plate_height),
    (foot_inset, -plate_height), (0, -shoulder_height),
]
plate = (
    cq.Workplane("XZ")
    .polyline(plate_outline).close().extrude(-plate_thickness)
)
plate_edge_radius = 0.635
plate = plate.faces("<Y").edges("not (|X or |Z)").fillet(plate_edge_radius)
through_holes = (
    cq.Workplane("XZ")
    .pushPoints(mounting_holes).circle(clearance_radius)
    .pushPoints(alignment_holes + lower_holes).circle(hole_radius)
    .extrude(-plate_thickness)
)
plate = plate.cut(through_holes)
pin_height = 44.45
pin_center = (plate_width / 2, -pin_height)
pin_radius = 2.413
pin_length = 9.906
pin = (
    cq.Workplane("XZ", origin=(0, plate_thickness, 0))
    .moveTo(*pin_center).circle(pin_radius).extrude(-pin_length)
)
plate = plate.union(pin)

cover_margin = 3.175
cover_left = -3.227521
cover_right = plate_width + cover_margin
cover_top = cover_margin
cover_bottom = -plate_height - cover_margin
cover_depth = 12.7
cover_notch_left = 25.347479
side_slope = foot_inset / shoulder_height
side_offset = foot_inset + cover_margin * math.sqrt(1 + side_slope ** 2)
cover_left_shoulder = (-side_offset - cover_left) / side_slope
cover_right_shoulder = (cover_right - plate_width - side_offset) / side_slope
cover_left_foot = -side_offset - side_slope * cover_bottom
cover_right_foot = plate_width - cover_left_foot
cover_outline = [
    (cover_left, cover_top), (cover_notch_left, cover_top),
    (cover_notch_left, -notch_depth), (notch_right, -notch_depth),
    (notch_right, cover_top), (cover_right, cover_top),
    (cover_right, cover_right_shoulder), (cover_right_foot, cover_bottom),
    (cover_left_foot, cover_bottom), (cover_left, cover_left_shoulder),
]
cover = (
    cq.Workplane("XZ", origin=(0, plate_thickness, 0))
    .polyline(cover_outline).close().extrude(-cover_depth)
)

cover_side_radius = plate_thickness
cover_bottom_radius = 2.54
cover_top_radius = 1.27
cover_back_y = plate_thickness + cover_depth
cover = (
    cover.faces(">Y").edges("not |X")
    .filter(lambda edge: edge.Center().z < -notch_depth)
    .fillet(cover_side_radius)
)
for x, z in ((cover_left, cover_left_shoulder), (cover_right, cover_right_shoulder)):
    cover = round_edges(cover, cover_side_radius,
                        (x, plate_thickness + cover_side_radius / 2, z))
cover = round_edges(cover, cover_bottom_radius,
                    (plate_width / 2, cover_back_y, cover_bottom))
for x in ((cover_left + cover_notch_left) / 2, (notch_right + cover_right) / 2):
    cover = round_edges(cover, cover_top_radius, (x, cover_back_y, cover_top))
cover_hole_depth = 4.445
cover_holes = (
    cq.Workplane("XZ", origin=(0, plate_thickness, 0))
    .pushPoints(mounting_holes).circle(clearance_radius)
    .pushPoints(alignment_holes + lower_holes).circle(hole_radius)
    .extrude(-cover_hole_depth)
)
cover = cover.cut(cover_holes)
cover_notch_angle = 15
cover_notch_width = 25.4
notch_cut = (
    cq.Workplane("YZ", origin=(cover_notch_left, 0, 0))
    .polyline([
        (plate_thickness, -notch_depth),
        (cover_back_y, -notch_depth),
        (cover_back_y, -notch_depth - cover_depth
            * math.tan(math.radians(cover_notch_angle))),
    ]).close().extrude(cover_notch_width)
)
cover = cover.cut(notch_cut)
pin_clearance_radius = 2.54
pin_counterbore_radius = 6.35
pin_counterbore_depth = plate_thickness
pin_clearance = (
    cq.Workplane("XZ", origin=(0, plate_thickness, 0))
    .moveTo(*pin_center).circle(pin_clearance_radius).extrude(-cover_depth)
)
pin_counterbore = (
    cq.Workplane("XZ", origin=(0, cover_back_y, 0))
    .moveTo(*pin_center).circle(pin_counterbore_radius).extrude(pin_counterbore_depth)
)
cover = cover.cut(pin_clearance).cut(pin_counterbore)

crossbar_top = -plate_thickness
crossbar_bottom = -28.448
crossbar_height = crossbar_top - crossbar_bottom
crossbar = (
    cq.Workplane("XY")
    .box(plate_width, plate_thickness, crossbar_height, centered=False)
    .translate((0, -plate_thickness, crossbar_bottom))
)
crossbar_holes = (
    cq.Workplane("XZ")
    .pushPoints(mounting_holes).circle(clearance_radius)
    .pushPoints(alignment_holes).circle(hole_radius).extrude(plate_thickness)
)
crossbar = crossbar.cut(crossbar_holes)
top_hole_centers = [
    (plate_thickness, -plate_thickness / 2),
    (3 * plate_thickness, -plate_thickness / 2),
]
top_holes = (
    cq.Workplane("XY", origin=(0, 0, crossbar_top))
    .pushPoints(top_hole_centers).circle(hole_radius).extrude(-plate_thickness)
)
bottom_hole_depth = 7.62
bottom_hole_center = (2 * plate_thickness, -plate_thickness / 2)
bottom_hole = (
    cq.Workplane("XY", origin=(0, 0, crossbar_bottom))
    .moveTo(*bottom_hole_center).circle(hole_radius).extrude(bottom_hole_depth)
)
crossbar = crossbar.cut(top_holes).cut(bottom_hole)

front_block_width = plate_width / 2
front_block_depth = 8.4328
front_block = (
    cq.Workplane("XY")
    .box(front_block_width, front_block_depth, crossbar_height, centered=False)
    .translate((0, -plate_thickness - front_block_depth, crossbar_bottom))
)
front_holes = (
    cq.Workplane("XZ", origin=(0, -plate_thickness, 0))
    .pushPoints(mounting_holes).circle(hole_radius).extrude(front_block_depth)
)
front_block = front_block.cut(front_holes)

top_bracket_width = 30.48
bracket_depth = 20.32
bracket_flat_depth = 11.43
bracket_slope_angle = 10
top_lip_width = 2.54
top_lip_height = 2.54
top_bracket = (
    cq.Workplane("XY")
    .box(top_bracket_width, bracket_depth, plate_thickness, centered=False)
    .translate((0, -bracket_depth, -plate_thickness))
)
bracket_slope_cut = (
    cq.Workplane("YZ")
    .polyline([
        (-bracket_flat_depth, 0), (-bracket_depth, 0),
        (-bracket_depth, -(bracket_depth - bracket_flat_depth)
            * math.tan(math.radians(bracket_slope_angle))),
    ]).close().extrude(top_bracket_width - top_lip_width)
)
top_bracket = top_bracket.cut(bracket_slope_cut)
bracket_slope_drop = (
    (bracket_depth - bracket_flat_depth) * math.tan(math.radians(bracket_slope_angle))
)
top_bracket = round_edges(
    top_bracket, cover_top_radius,
    (top_bracket_width / 2, -bracket_depth, -plate_thickness),
    (0, -bracket_depth, -plate_thickness / 2),
    ((top_bracket_width - top_lip_width) / 2, -bracket_depth, -bracket_slope_drop),
)
top_lip = (
    cq.Workplane("XY")
    .box(top_lip_width, bracket_depth, top_lip_height, centered=False)
    .translate((top_bracket_width - top_lip_width, -bracket_depth, 0))
)
top_bracket = top_bracket.union(top_lip)
top_slot_length = 7.62
top_slots = (
    cq.Workplane("XY")
    .pushPoints(top_hole_centers)
    .slot2D(top_slot_length, 2 * hole_radius).extrude(-plate_thickness)
)
top_bracket = top_bracket.cut(top_slots)

bottom_bracket_left = 1.27
bottom_bracket_width = 20.32
bottom_bracket_tip_width = 12.7
bottom_bracket_thickness = 3.175
bottom_bracket_radius = 0.635
bottom_bracket_right = bottom_bracket_left + bottom_bracket_width
bottom_bracket_tip_right = bottom_bracket_left + bottom_bracket_tip_width
bottom_bracket = (
    cq.Workplane("XY", origin=(0, 0, crossbar_bottom))
    .polyline([
        (bottom_bracket_left, 0), (bottom_bracket_right, 0),
        (bottom_bracket_right, -bracket_flat_depth),
        (bottom_bracket_tip_right, -bracket_flat_depth),
        (bottom_bracket_tip_right, -bracket_depth),
        (bottom_bracket_left, -bracket_depth),
    ]).close().extrude(-bottom_bracket_thickness)
)
bottom_bracket_z = crossbar_bottom - bottom_bracket_thickness
bottom_slope_cut = (
    cq.Workplane("YZ", origin=(bottom_bracket_left, 0, 0))
    .polyline([
        (-bracket_flat_depth, bottom_bracket_z), (-bracket_depth, bottom_bracket_z),
        (-bracket_depth, bottom_bracket_z + (bracket_depth
            - bracket_flat_depth) * math.tan(math.radians(bracket_slope_angle))),
    ]).close().extrude(bottom_bracket_tip_width)
)
bottom_bracket = bottom_bracket.cut(bottom_slope_cut)
bottom_bracket_tip_center = bottom_bracket_left + bottom_bracket_tip_width / 2
bottom_bracket_edge_z = crossbar_bottom - bottom_bracket_thickness / 2
bottom_bracket = round_edges(
    bottom_bracket, bottom_bracket_radius,
    (bottom_bracket_tip_center, -bracket_depth, crossbar_bottom),
    (bottom_bracket_left, -bracket_depth, bottom_bracket_edge_z),
    (bottom_bracket_tip_right, -bracket_depth, bottom_bracket_edge_z),
    (bottom_bracket_tip_center, -bracket_depth, bottom_bracket_z + bracket_slope_drop),
)
bottom_bracket_hole = (
    cq.Workplane("XY", origin=(0, 0, crossbar_bottom))
    .moveTo(*bottom_hole_center).circle(hole_radius).extrude(-bottom_bracket_thickness)
)
bottom_bracket = bottom_bracket.cut(bottom_bracket_hole)

rod_radius = 1.27
rod_inset = 9.525
rod_x = cover_notch_left - rod_inset
rod_y = 12.7
rod_top = -28.575
rod_bend_z = -116.205
rod_tip_angle = 30
rod_tip_length = rod_radius / math.tan(math.radians(rod_tip_angle))
rod_end_z = rod_bend_z - rod_radius
rod_path = (
    cq.Workplane("YZ", origin=(rod_x, 0, 0))
    .moveTo(rod_y, rod_top).lineTo(rod_y, rod_bend_z)
    .radiusArc((rod_y - rod_radius, rod_end_z), rod_radius)
    .lineTo(rod_tip_length, rod_end_z)
)
rod = (
    cq.Workplane("XY", origin=(rod_x, rod_y, rod_top))
    .circle(rod_radius).sweep(rod_path)
)
rod_tip = cq.Solid.makeCone(
    rod_radius, 0, rod_tip_length,
    cq.Vector(rod_x, rod_tip_length, rod_end_z), cq.Vector(0, -1, 0),
)
rod = rod.union(rod_tip)
cover = cover.cut(rod)

cross_pin_radius = 0.8128
cross_pin_length = 25.4
cross_pin_start = cover_notch_left - cross_pin_length / 2
cross_pin_y = 16.51
cross_pin_z = -6.985
cross_pin_end = cross_pin_start + cross_pin_length - cross_pin_radius
cross_pin = (
    cq.Workplane("YZ", origin=(cross_pin_start, cross_pin_y, cross_pin_z))
    .circle(cross_pin_radius).extrude(cross_pin_length - cross_pin_radius)
)
cross_pin = cross_pin.union(
    cq.Workplane("XY", origin=(cross_pin_end, cross_pin_y, cross_pin_z))
    .sphere(cross_pin_radius)
)
cover = cover.cut(cross_pin)

latch_radius = 1.27
latch_start_x = 19.05
latch_length = 25.4
latch_y = -plate_thickness
latch_z = -20.828
latch = (
    cq.Workplane("YZ", origin=(latch_start_x, latch_y, latch_z))
    .circle(latch_radius).extrude(latch_length)
)
for x in (latch_start_x, latch_start_x + latch_length):
    latch = latch.union(
        cq.Workplane("XY", origin=(x, latch_y, latch_z))
        .sphere(latch_radius)
    )
latch = (
    latch.copyWorkplane(cq.Workplane("XZ", origin=(0, latch_y, 0))).split(keepTop=True)
)
latch_stem_extension = 0.016302
latch_stem = (
    cq.Workplane("XZ", origin=(latch_start_x + latch_stem_extension / 2, 0, latch_z))
    .slot2D(2 * latch_radius + latch_stem_extension, 2 * latch_radius)
    .extrude(plate_thickness)
)
latch = latch.union(latch_stem)
front_block = front_block.cut(latch)
latch_hole = (
    cq.Workplane("XZ", origin=(latch_start_x, 0, latch_z))
    .circle(latch_radius).extrude(plate_thickness)
)
crossbar = crossbar.cut(latch_hole)

spring_radius = 0.81407
spring_y = 7.18865
spring_bend_radius = 3.31289
spring_corner_radius = 1.21739
spring_top_z = 0.77289
spring_start_x = 29.970279
spring_top_end_x = 43.127479
spring_side_x = spring_top_end_x + spring_corner_radius
spring_side_top_z = spring_top_z - spring_corner_radius
spring_bottom_z = pin_center[1] - spring_bend_radius
spring_bottom_corner_x = spring_side_x - spring_bend_radius
spring_path = (
    cq.Workplane("XZ", origin=(0, spring_y, 0))
    .moveTo(spring_start_x, spring_top_z).lineTo(spring_top_end_x, spring_top_z)
    .radiusArc((spring_side_x, spring_side_top_z), spring_corner_radius)
    .lineTo(spring_side_x, pin_center[1])
    .radiusArc((spring_bottom_corner_x, spring_bottom_z), spring_bend_radius)
    .lineTo(pin_center[0], spring_bottom_z)
    .threePointArc((pin_center[0] - spring_bend_radius, pin_center[1]),
                   (pin_center[0] + spring_bend_radius, pin_center[1]))
)
spring = (
    cq.Workplane("YZ", origin=(spring_start_x, spring_y, spring_top_z))
    .circle(spring_radius).sweep(spring_path)
)
spring = spring.union(
    cq.Workplane("XY", origin=(spring_start_x, spring_y, spring_top_z))
    .sphere(cross_pin_radius)
)

groove_depth = 1.651
groove_ring_radius = 4.191
groove_side_x = 49.53
groove_turn_x = 45.69374
groove_turn_z = -46.885619
groove_outer_radius = 4.981302
groove_inner_radius = 4.855318
groove_right_x = groove_side_x + groove_depth / 2
groove_left_x = groove_side_x - groove_depth / 2
groove_bottom_z = pin_center[1] - groove_ring_radius
groove_top_z = groove_bottom_z + groove_depth
groove_outer_top_z = (
    groove_turn_z + math.sqrt(
        groove_outer_radius ** 2 - (groove_right_x - groove_turn_x) ** 2
    )
)
groove_outer_bottom_x = (
    groove_turn_x - math.sqrt(
        groove_outer_radius ** 2 - (groove_bottom_z - groove_turn_z) ** 2
    )
)
groove_inner_top_z = (
    groove_turn_z + math.sqrt(
        groove_inner_radius ** 2 - (groove_left_x - groove_turn_x) ** 2
    )
)
groove_inner_bottom_x = (
    groove_turn_x - math.sqrt(
        groove_inner_radius ** 2 - (groove_top_z - groove_turn_z) ** 2
    )
)
groove_ring_end_x = (
    pin_center[0] + math.sqrt(
        groove_ring_radius ** 2 - (groove_top_z - pin_center[1]) ** 2
    )
)
spring_groove = (
    cq.Workplane("XZ", origin=(0, plate_thickness, 0))
    .moveTo(groove_right_x, -notch_depth).lineTo(groove_right_x, groove_outer_top_z)
    .threePointArc((groove_turn_x + groove_outer_radius, groove_turn_z),
                   (groove_outer_bottom_x, groove_bottom_z))
    .lineTo(pin_center[0], groove_bottom_z)
    .threePointArc((pin_center[0] - groove_ring_radius, pin_center[1]),
                   (groove_ring_end_x, groove_top_z))
    .lineTo(groove_inner_bottom_x, groove_top_z)
    .threePointArc((groove_turn_x, groove_turn_z - groove_inner_radius),
                   (groove_left_x, groove_inner_top_z))
    .lineTo(groove_left_x, -notch_depth).close().extrude(-groove_depth)
)
cover = cover.cut(spring_groove)

leg_height = plate_height + crossbar_bottom
leg_center_x = plate_width / 2
right_leg_top_width = 15.24
right_leg_bottom_width = 21.59
right_leg_top_depth = 8.89
right_leg_bottom_depth = 5.08
right_leg = (
    cq.Workplane("XZ")
    .polyline([
        (leg_center_x, crossbar_bottom),
        (leg_center_x + right_leg_top_width, crossbar_bottom),
        (leg_center_x + right_leg_bottom_width, -plate_height),
        (leg_center_x, -plate_height),
    ]).close().extrude(right_leg_top_depth)
)
right_leg_wedge = (
    cq.Workplane("YZ")
    .polyline([
        (0, crossbar_bottom), (-right_leg_top_depth, crossbar_bottom),
        (-right_leg_bottom_depth, -plate_height), (0, -plate_height),
    ]).close().extrude(plate_width)
)
right_leg = right_leg.intersect(right_leg_wedge)
left_leg_top_width = 7.62
left_leg_ankle_x = 20.32
left_leg_ankle_z = -59.69
left_leg_toe_x = 10.16
left_leg_toe_top_x = 10.185982
left_leg_toe_thickness = 1.27
left_leg_top_depth = 12.2428
left_leg_bottom_depth = 16.0528
left_leg = (
    cq.Workplane("XZ")
    .polyline([
        (leg_center_x, crossbar_bottom), (leg_center_x, -plate_height),
        (left_leg_toe_x, -plate_height),
        (left_leg_toe_top_x, -plate_height + left_leg_toe_thickness),
        (left_leg_ankle_x, left_leg_ankle_z),
        (leg_center_x - left_leg_top_width, crossbar_bottom),
    ]).close().extrude(left_leg_bottom_depth)
)
left_leg_wedge = (
    cq.Workplane("YZ")
    .polyline([
        (0, crossbar_bottom), (-left_leg_top_depth, crossbar_bottom),
        (-left_leg_bottom_depth, -plate_height), (0, -plate_height),
    ]).close().extrude(plate_width)
)
left_leg = left_leg.intersect(left_leg_wedge)
left_leg_holes = (
    cq.Workplane("XZ")
    .pushPoints(lower_holes[:2])
    .circle(hole_radius).extrude(plate_thickness)
)
right_leg_hole_depth = 2.54
right_leg_holes = (
    cq.Workplane("XZ")
    .pushPoints(lower_holes[2:])
    .circle(hole_radius).extrude(right_leg_hole_depth)
)
left_leg = left_leg.cut(left_leg_holes)
right_leg = right_leg.cut(right_leg_holes)

notch_tip_z = -50.8
notch_axis_slope = 0.08678913
notch_blend_radius = 5.08
notch_lower_corner_x = 30.48
notch_lower_corner_z = -62.23
notch_left_slope = (
    (leg_center_x - notch_lower_corner_x) / (notch_tip_z - notch_lower_corner_z)
)
notch_exit_angle = 45
leg_depth_slope = (right_leg_top_depth - right_leg_bottom_depth) / leg_height
notch_plane_stretch = math.sqrt(1 + leg_depth_slope ** 2)
notch_tip_y = -right_leg_top_depth + (crossbar_bottom - notch_tip_z) * leg_depth_slope
notch_plane = cq.Plane(
    origin=(leg_center_x, notch_tip_y, notch_tip_z),
    xDir=(1, 0, 0), normal=(0, 1, leg_depth_slope),
)
notch_axis = (notch_axis_slope, notch_plane_stretch)
notch_side_offset = leg_center_x - notch_tip_z * notch_left_slope
notch_exit_offset = notch_lower_corner_x - notch_lower_corner_z
notch_circle_side = (
    notch_side_offset - notch_blend_radius * math.sqrt(
        1 + notch_left_slope ** 2
    )
)
notch_circle_exit = notch_exit_offset - notch_blend_radius * math.sqrt(2)
notch_circle_z = (notch_circle_side - notch_circle_exit) / (1 - notch_left_slope)
notch_circle_x = notch_circle_exit + notch_circle_z
notch_tangent_x = (
    notch_circle_x + notch_blend_radius / math.sqrt(
        1 + notch_left_slope ** 2
    )
)
notch_tangent_z = (
    notch_circle_z - notch_blend_radius * notch_left_slope / math.sqrt(
        1 + notch_left_slope ** 2
    )
)
notch_tool_bottom = -plate_height - 2 * plate_thickness
notch_tool_height = (notch_tip_z - notch_tool_bottom) * notch_plane_stretch
notch_profile = (
    cq.Workplane(notch_plane)
    .moveTo(0, 0)
    .lineTo(
        notch_tangent_x - leg_center_x,
        (notch_tip_z - notch_tangent_z) * notch_plane_stretch,
    )
    .ellipseArc(notch_blend_radius, notch_blend_radius * notch_plane_stretch,
                math.degrees(math.atan(notch_left_slope)), notch_exit_angle)
    .lineTo(notch_tool_bottom + notch_exit_offset - leg_center_x, notch_tool_height)
    .lineTo(notch_tool_height * notch_axis[0] / notch_axis[1], notch_tool_height)
    .close()
)
notch_tool = notch_profile.revolve(360, (0, 0), notch_axis)
notch_back = (
    cq.Workplane("XZ")
    .add(notch_tool.section().wires().vals())
    .toPending().extrude(left_leg_bottom_depth)
)
notch_tool = notch_tool.union(notch_back)
left_leg = left_leg.cut(notch_tool)
modeling_tolerance = 0.0001
notch_mouth_radius = 1.27
right_leg = right_leg.cut(notch_tool.translate((-modeling_tolerance, 0, 0)))
notch_edge_z = (notch_tip_z + notch_tangent_z) / 2
notch_edge_y = -right_leg_top_depth + (crossbar_bottom - notch_edge_z) * leg_depth_slope
notch_edge_x = leg_center_x + (notch_tip_z - notch_edge_z) * 2 * notch_axis_slope
right_leg = round_edges(right_leg, notch_mouth_radius,
                        (notch_edge_x, notch_edge_y, notch_edge_z))

solid = (
    cq.Workplane("XY")
    .add(cq.Compound.makeCompound([
        plate.val(), cover.val(), crossbar.val(), front_block.val(),
        top_bracket.val(), bottom_bracket.val(), rod.val(), cross_pin.val(),
        latch.val(), spring.val(), left_leg.val(), right_leg.val(),
    ]).scale(scale))
)
show_object(solid)
