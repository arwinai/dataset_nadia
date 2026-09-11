import math
import cadquery as cq

teeth = 40
module = 2.54
pressure_angle = 14.5
addendum_factor = 1.0
dedendum_factor = 1.22

pitch_half_tooth_angle = 2.230334
flank_radius = 20.156967
fillet_radius = 1.004568
gear_rotation = -133.4584533

gear_thickness = 11.43
hub_radius = 19.05
hub_length = 12.7
bore_radius = 12.7
scale = 0.001


def polar(radius, angle):
    angle = math.radians(angle)
    return cq.Vector(radius * math.cos(angle), radius * math.sin(angle))


def direction(center, target):
    return math.degrees(math.atan2(target.y - center.y, target.x - center.x)) % 360


def axis_angle(radius, distance):
    return math.degrees(math.acos((radius ** 2 + base_radius ** 2 - distance ** 2)
                                 / (2 * radius * base_radius)))


step = 360 / teeth
origin = cq.Vector(0, 0, 0)
pitch_radius = module * teeth / 2
tip_radius = pitch_radius + addendum_factor * module
root_radius = pitch_radius - dedendum_factor * module
base_radius = pitch_radius * math.cos(math.radians(pressure_angle))
fillet_center_radius = root_radius + fillet_radius

flank_angle = axis_angle(pitch_radius, flank_radius) - pitch_half_tooth_angle
tip_angle = axis_angle(tip_radius, flank_radius) - flank_angle
fillet_angle = axis_angle(fillet_center_radius, flank_radius + fillet_radius) - flank_angle

flank_center = polar(base_radius, -flank_angle)
fillet_center = polar(fillet_center_radius, fillet_angle)

half = [cq.Edge.makeCircle(tip_radius, origin,
                          angle1=0, angle2=tip_angle),
        cq.Edge.makeCircle(flank_radius, flank_center,
                          angle1=direction(flank_center, polar(tip_radius, tip_angle)),
                          angle2=direction(flank_center, fillet_center)),
        cq.Edge.makeCircle(fillet_radius, fillet_center,
                          angle1=direction(fillet_center, origin),
                          angle2=direction(fillet_center, flank_center)),
        cq.Edge.makeCircle(root_radius, origin,
                          angle1=fillet_angle, angle2=step / 2)]
tooth = half + [edge.mirror("XZ") for edge in half]
outline = cq.Wire.assembleEdges([edge.rotate((0, 0, 0), (0, 0, 1), gear_rotation + i * step)
                                for i in range(teeth) for edge in tooth])

body = (cq.Workplane("XY").add(outline).toPending()
        .extrude(gear_thickness))
hub = (cq.Workplane("XY", origin=(0, 0, -hub_length))
       .circle(hub_radius).extrude(hub_length))
bore = (cq.Workplane("XY", origin=(0, 0, -hub_length))
        .circle(bore_radius).extrude(hub_length + gear_thickness))

solid = body.union(hub).cut(bore)
solid = cq.Workplane("XY").add(solid.val().scale(scale))

show_object(solid)
