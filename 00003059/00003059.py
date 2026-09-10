import math
import cadquery as cq

teeth = 15
pitch = 15.875
height = 8.7122
bore_radius = 15.875
tip_rise = 4.7625
root_radius = 5.1435
flank_radius = 13.2715
tip_radius = 8.48
root_angle = 27.0
flank_angle = 12 + 44 / 60
bevel_width = 7.9375
bevel_depth = 1.984375
scale = 0.001


def polar(radius, angle):
    angle = math.radians(angle)
    return cq.Vector(radius * math.cos(angle), radius * math.sin(angle))


step = 360 / teeth
half_height = height / 2
root_center = cq.Vector(-pitch / 2,
                       -pitch / (2 * math.tan(math.radians(step / 2))))
outer_radius = -root_center.y + tip_rise
flank_center = root_center + polar(root_radius - flank_radius, root_angle)
flank_end = flank_center + polar(flank_radius, flank_angle)

tip_y = root_center.y - polar(tip_radius, flank_angle).y
tip_x = flank_end.x - (tip_y - flank_end.y) * math.tan(math.radians(flank_angle))
tip_start = cq.Vector(tip_x, tip_y)
tip_center = tip_start + polar(tip_radius, flank_angle)

center_distance = tip_center.Length
chord_offset = ((outer_radius ** 2 - tip_radius ** 2 + center_distance ** 2)
                / (2 * center_distance))
chord_half = math.sqrt(outer_radius ** 2 - chord_offset ** 2)
center_axis = tip_center.normalized()
chord_axis = cq.Vector(center_axis.y, -center_axis.x)
tip_end = center_axis * chord_offset + chord_axis * chord_half
tip_angle = math.degrees(math.atan2(tip_end.y - tip_center.y,
                                   tip_end.x - tip_center.x)) % 360

half = [cq.Edge.makeCircle(root_radius, root_center,
                          angle1=root_angle, angle2=90 - step / 2),
        cq.Edge.makeCircle(flank_radius, flank_center,
                          angle1=flank_angle, angle2=root_angle),
        cq.Edge.makeLine(flank_end, tip_start),
        cq.Edge.makeCircle(tip_radius, tip_center,
                          angle1=180 + flank_angle, angle2=tip_angle)]
crest = cq.Edge.makeThreePointArc(tip_end, cq.Vector(0, -outer_radius),
                                 cq.Vector(-tip_end.x, tip_end.y))
tooth = half + [edge.mirror("YZ") for edge in half] + [crest]
outline = cq.Wire.assembleEdges([edge.rotate((0, 0, 0), (0, 0, 1), i * step)
                                for i in range(teeth) for edge in tooth])

body = (cq.Workplane("XY").add(outline).toPending()
        .extrude(height).translate((0, 0, -half_height)))

face_radius = outer_radius - bevel_width
half_tip = half_height - bevel_depth
outside = (cq.Workplane("XZ")
           .polyline([(0, -half_height),
                      (face_radius, -half_height),
                      (outer_radius, -half_tip),
                      (outer_radius, half_tip),
                      (face_radius, half_height),
                      (0, half_height)])
           .close().revolve())
bore = (cq.Workplane("XY", origin=(0, 0, -half_height))
        .circle(bore_radius).extrude(height))

solid = body.intersect(outside).cut(bore)
solid = cq.Workplane("XY").add(solid.val().scale(scale))

show_object(solid)
