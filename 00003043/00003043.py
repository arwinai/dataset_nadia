from dataclasses import dataclass

import cadquery as cq

length = 0.2286
base_z = -0.4572
bore_radius = 0.0033274

outer_half_width = 0.01905
web_offset = 0.0067564
mouth_half_width = 0.004064
lip_tangent = 0.0056176176
lip_base = 0.014986
top_slot_back = 0.010287
side_slot_back = 0.010287043
notch_bottom = 0.018231251


@dataclass(frozen=True)
class Segment:
    end: tuple
    via: tuple | None = None


top_slot = {
    "floor": Segment(end=(0.001902184, web_offset)),
    "floor_round": Segment(end=(0.005252158, 0.008144007), via=(0.0037151774, 0.0071170274)),
    "diagonal": Segment(end=(0.010022899, 0.01291476)),
    "back_round": Segment(end=(top_slot_back, 0.0135523574), via=(0.0102183626, 0.013207292)),
    "back_wall": Segment(end=(top_slot_back, 0.0140843)),
    "lip_round": Segment(end=(0.0093853, lip_base), via=(0.010022898, 0.014721898)),
    "lip": Segment(end=(lip_tangent, lip_base)),
    "inner_round": Segment(end=(mouth_half_width, 0.0165396184), via=(0.004519044, 0.0154410443)),
    "mouth": Segment(end=(mouth_half_width, 0.017496383)),
    "outer_round": Segment(end=(lip_tangent, outer_half_width), via=(0.004519044, 0.018594956)),
}

upper_corner = {
    "top_edge": Segment(end=(0.0079741785, outer_half_width)),
    "top_notch": Segment(end=(0.009498179, outer_half_width), via=(0.008736179, 0.018288)),
    "corner_edge": Segment(end=(0.014327719, outer_half_width)),
    "corner_notch": Segment(end=(0.0158474874, outer_half_width), via=(0.015087603, notch_bottom)),
    "corner_round": Segment(end=(outer_half_width, 0.01584751), via=(0.018120176, 0.018120192)),
    "side_corner_notch": Segment(end=(outer_half_width, 0.014327741), via=(notch_bottom, 0.0150876254)),
    "side_edge": Segment(end=(outer_half_width, 0.009496092)),
    "side_notch": Segment(end=(outer_half_width, 0.0079763234), via=(notch_bottom, 0.0087362076)),
    "slot_edge": Segment(end=(outer_half_width, lip_tangent)),
}

right_slot = {
    "outer_round": Segment(end=(0.017496383, mouth_half_width), via=(0.018594956, 0.004519044)),
    "mouth": Segment(end=(0.0165396184, mouth_half_width)),
    "inner_round": Segment(end=(lip_base, lip_tangent), via=(0.0154410443, 0.004519044)),
    "lip": Segment(end=(lip_base, 0.009385343)),
    "lip_round": Segment(end=(0.0140843, side_slot_back), via=(0.014721898, 0.010022941)),
    "back_wall": Segment(end=(0.0135160424, side_slot_back)),
    "back_round": Segment(end=(0.012878443, 0.01002294), via=(0.013170976, 0.0102184045)),
    "diagonal": Segment(end=(0.0081475796, 0.0052920654)),
    "floor_round": Segment(end=(web_offset, 0.0019334536), via=(0.007117956, 0.0037511206)),
}

lower_corner = {
    "side_edge": Segment(end=(outer_half_width, -0.007976319)),
    "side_notch": Segment(end=(outer_half_width, -0.009496086), via=(notch_bottom, -0.0087362024)),
    "corner_edge": Segment(end=(outer_half_width, -0.014327743)),
    "side_corner_notch": Segment(end=(outer_half_width, -0.0158475116), via=(notch_bottom, -0.015087627)),
    "corner_round": Segment(end=(0.0158474874, -outer_half_width), via=(0.0181201754, -0.018120193)),
    "bottom_corner_notch": Segment(end=(0.014327719, -outer_half_width), via=(0.015087603, -notch_bottom)),
    "bottom_edge": Segment(end=(0.009496062, -outer_half_width)),
    "bottom_notch": Segment(end=(0.0079762945, -outer_half_width), via=(0.0087361784, -notch_bottom)),
    "slot_edge": Segment(end=(lip_tangent, -outer_half_width)),
}


def reflect(point):
    x, y = point
    return x, -y


def draw_section(workplane, section, start, reverse=False, mirrored=False):
    segments = list(section.values())
    starts = [start] + [segment.end for segment in segments[:-1]]
    traversal = list(zip(starts, segments))
    if reverse:
        traversal.reverse()
    for previous, segment in traversal:
        end = previous if reverse else segment.end
        via = segment.via
        if mirrored:
            end = reflect(end)
            via = reflect(via) if via is not None else None
        if via is None:
            workplane = workplane.lineTo(*end)
        else:
            workplane = workplane.threePointArc(via, end)
    return workplane


top_start = (0, web_offset)
side_start = (outer_half_width, lip_tangent)
side_floor = right_slot["floor_round"].end

profile = cq.Workplane("XY", origin=(0, 0, base_z)).moveTo(*top_start)
profile = draw_section(profile, top_slot, top_start)
profile = draw_section(profile, upper_corner, top_slot["outer_round"].end)
profile = draw_section(profile, right_slot, side_start)
profile = profile.lineTo(*reflect(side_floor))
profile = draw_section(profile, right_slot, side_start, reverse=True, mirrored=True)
profile = draw_section(profile, lower_corner, reflect(side_start))
profile = draw_section(profile, top_slot, top_start, reverse=True, mirrored=True)

solid = (profile
         .mirrorY()
         .extrude(length)
         .faces(">Z")
         .workplane(centerOption="ProjectedOrigin")
         .hole(2 * bore_radius)
         )

show_object(solid)
