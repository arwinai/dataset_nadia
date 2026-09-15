import math
import cadquery as cq

plate_thickness = 25.0
ground_height = 22.291681
scale = 0.001

ground_plane = cq.Workplane("XY", origin=(0, 0, ground_height))

blade_angle = 15.0
blade_width = 249.94332
blade_end_along = 1975.53939
edge_fillet = 5.0

nose_radius = 220.0
nose_center_along = 197.59745
tip_radius = 200.0
corner_radius = 5.0
dip_start_along = 986.56845

notch_length = 100.0
notch_depth = plate_thickness
notch_along = nose_center_along + notch_length
notch_end_along = notch_along + notch_length
notch_center = (notch_along + notch_end_along) / 2
notch_bottom = blade_width - notch_depth

cut_clearance = plate_thickness
cut_thickness = plate_thickness + cut_clearance
blade_blank_end = blade_end_along + notch_length
nose_span = math.sqrt(nose_radius**2 - (blade_width - nose_radius)**2)
nose_end = (nose_center_along - nose_span, 0.0)
corner_along = blade_end_along - corner_radius
tip_along = blade_end_along - tip_radius
tip_end = (tip_along, blade_width)
dip_end = (dip_start_along, blade_width)

dip_rear_tangent = (1670.233618, 238.363343)
dip_rear_control = (1544.759963, 215.232982)
dip_rear_join = (1428.040158, 197.143426)
dip_floor_entry_control = (1301.051758, 177.462414)
dip_floor_exit_control = (1184.425228, 163.748167)
dip_front_join = (1115.399359, 177.363602)
dip_front_control = (1052.889778, 189.693691)
dip_front_tangent = (1029.417732, 224.436987)

blade_plane = cq.Workplane("XZ").transformed(rotate=(0, 0, blade_angle))

notch_cut = (
    blade_plane
    .center(notch_center, blade_width - notch_depth / 2 + cut_clearance / 2)
    .rect(notch_length, notch_depth + cut_clearance)
    .extrude(cut_thickness, both=True)
)

tip_cut = (
    blade_plane
    .moveTo(corner_along, 0.0)
    .radiusArc((blade_end_along, corner_radius), -corner_radius)
    .lineTo(blade_end_along, blade_width - tip_radius)
    .radiusArc(tip_end, -tip_radius)
    .lineTo(blade_blank_end, blade_width + cut_clearance)
    .lineTo(blade_blank_end, -cut_clearance)
    .lineTo(corner_along, -cut_clearance)
    .close()
    .extrude(cut_thickness, both=True)
)

blade = (
    blade_plane
    .moveTo(blade_blank_end, blade_width)
    .lineTo(*tip_end)
    .bezier([dip_rear_tangent, dip_rear_control, dip_rear_join],
            includeCurrent=True)
    .bezier([dip_floor_entry_control, dip_floor_exit_control, dip_front_join],
            includeCurrent=True)
    .bezier([dip_front_control, dip_front_tangent, dip_end],
            includeCurrent=True)
    .lineTo(nose_center_along, blade_width)
    .radiusArc(nose_end, -nose_radius)
    .lineTo(blade_blank_end, 0.0)
    .close()
    .extrude(plate_thickness)
)

rounded_edges = (
    cq.selectors.ParallelDirSelector(blade_plane.plane.xDir)
    + cq.selectors.TypeSelector("CIRCLE")
)

blade = (
    blade.faces("|Y").edges(rounded_edges)
    .filter(lambda edge: blade_plane.plane.toLocalCoords(edge.Center()).x < tip_along)
    .fillet(edge_fillet)
    .copyWorkplane(ground_plane).split(keepTop=True)
    .cut(notch_cut)
    .cut(tip_cut)
)

web_length = 500.0
web_start_y = web_length - plate_thickness
web_top_overhang = 0.27745
web_step_overhang = web_top_overhang * (notch_depth - edge_fillet) / notch_depth
web_step_level = blade_width - edge_fillet

web = (
    blade_plane
    .polyline([
        (notch_along, notch_bottom),
        (notch_end_along, notch_bottom),
        (notch_end_along, blade_width),
        (notch_along - web_top_overhang, blade_width),
        (notch_along - web_step_overhang, web_step_level),
        (notch_along, web_step_level),
    ])
    .close()
    .extrude(web_length)
    .translate((0, web_start_y, 0))
)

rail_angle = 4.9039606
rail_offset = 714.036676
rail_width = 200.0
rail_straight_start = 1330.030088

rail_tip_radius = 100.5281
rail_tip_center_along = 1790.371739
rail_tip_center_across = -100.161529
rail_tip_top_along = rail_tip_center_along + math.sqrt(
    rail_tip_radius**2 - rail_tip_center_across**2
)
rail_tip_bottom_along = rail_tip_center_along + math.sqrt(
    rail_tip_radius**2 - (rail_tip_center_across + rail_width)**2
)
rail_tip_top = (rail_tip_top_along, 0.0)
rail_tip_bottom = (rail_tip_bottom_along, -rail_width)

rail_nose_radius = 40.0
rail_nose_center_along = 802.404088
rail_nose_center_across = -74.24145
rail_front_along = 762.829795
rail_front_half_height = math.sqrt(
    rail_nose_radius**2 - (rail_nose_center_along - rail_front_along)**2
)
rail_front_bottom = (rail_front_along, rail_nose_center_across - rail_front_half_height)
rail_front_top = (rail_front_along, rail_nose_center_across + rail_front_half_height)

rail_outer_end = (rail_straight_start, -rail_width)
rail_outer_end_control = (1212.992344, -187.715442)
rail_outer_taper_control = (1096.715209, -171.971561)
rail_outer_taper_join = (999.813160, -154.580644)
rail_outer_round_control = (923.037553, -140.801801)
rail_outer_start_control = (858.424486, -125.989045)
rail_outer_round_join = (794.706599, -113.493823)

rail_inner_round_join = (809.182303, -34.819938)
rail_inner_round_control = (954.427523, -59.793728)
rail_inner_waist_control = (1101.400081, -57.781116)
rail_inner_taper_join = (1196.300856, -41.210295)
rail_inner_taper_control = (1253.353400, -31.248233)
rail_inner_end_control = (1291.586233, -16.024563)
rail_inner_end = (rail_straight_start, 0.0)

rail_plane = (
    cq.Workplane("XY")
    .transformed(rotate=(0, -rail_angle, 0))
    .workplane(offset=rail_offset)
)

rail = (
    rail_plane
    .moveTo(*rail_outer_end)
    .bezier([rail_outer_end_control, rail_outer_taper_control, rail_outer_taper_join],
            includeCurrent=True)
    .bezier([rail_outer_round_control, rail_outer_start_control, rail_outer_round_join],
            includeCurrent=True)
    .radiusArc(rail_front_bottom, rail_nose_radius)
    .lineTo(*rail_front_top)
    .radiusArc(rail_inner_round_join, rail_nose_radius)
    .bezier([rail_inner_round_control, rail_inner_waist_control, rail_inner_taper_join],
            includeCurrent=True)
    .bezier([rail_inner_taper_control, rail_inner_end_control, rail_inner_end],
            includeCurrent=True)
    .lineTo(*rail_tip_top)
    .radiusArc(rail_tip_bottom, rail_tip_radius)
    .close()
    .extrude(plate_thickness)
)

strut_start_along = 1733.20669
strut_width = 80.0
strut_end_along = strut_start_along + strut_width
strut_front_y = -plate_thickness
strut_back_y = strut_front_y - plate_thickness
strut_blank_height = 2 * max(blade_end_along, rail_offset)

strut = (
    blade_plane
    .center(strut_start_along + strut_width / 2, 0.0)
    .rect(strut_width, strut_blank_height)
    .extrude(plate_thickness)
    .translate((0, strut_front_y, 0))
    .copyWorkplane(ground_plane).split(keepTop=True)
    .copyWorkplane(rail_plane).split(keepBottom=True)
)

brace_height = 75.0
brace_center_y = strut_back_y - plate_thickness / 2
relative_angle = math.radians(blade_angle - rail_angle)
brace_end_along = (
    strut_end_along - rail_offset * math.sin(relative_angle)
) / math.cos(relative_angle)

brace = (
    rail_plane
    .workplane(offset=-brace_height)
    .center((rail_front_along + brace_end_along) / 2, brace_center_y)
    .rect(brace_end_along - rail_front_along, plate_thickness)
    .extrude(brace_height)
)

solid = cq.Compound.makeCompound([
    blade.val(), rail.union(strut).val(), web.val(), brace.val()
])
solid = cq.Workplane("XY").add(solid.scale(scale))

show_object(solid)
