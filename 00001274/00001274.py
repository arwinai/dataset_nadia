import math
import cadquery as cq

wall = 3.0
hole_radius = 5.0
lobe_radius = hole_radius + wall
hole_chamfer = 1.0
rib_width = wall
base_height = wall
fillet_radius = 2.5
height = 15.0
scale = 0.001

hole_centers = [(0.0, 0.0), (57.45383, 48.21026), (-57.56869, 48.07153)]
lobe_centers = [(0.0, 0.0), (57.45377, 48.21024), (-57.53289, 48.05707)]
blend_radii = [100.0, 125.0, 100.0]
ribs = [((0.0, 25.3556), 0.0),
        ((29.7590, 22.4147), 126.98915),
        ((-30.0210, 22.1780), 53.53455)]
sharp_joints = [(2, 1)]

middle = cq.Vector(sum(x for x, y in lobe_centers) / 3,
                   sum(y for x, y in lobe_centers) / 3)
overrun = 4 * max(math.hypot(x, y) for x, y in lobe_centers)

blend_centers = []
for i, blend_radius in enumerate(blend_radii):
    first = cq.Vector(*lobe_centers[i])
    second = cq.Vector(*lobe_centers[(i + 1) % 3])
    span = (second - first).Length
    along = (second - first).normalized()
    across = cq.Vector(-along.y, along.x)
    offset = math.sqrt((blend_radius + lobe_radius) ** 2 - (span / 2) ** 2)
    sides = [(first + second) * 0.5 + across * offset,
             (first + second) * 0.5 - across * offset]
    blend_centers.append(max(sides, key=lambda point: (point - middle).Length))

sharp_corners = []
for lobe, blend in sharp_joints:
    center = cq.Vector(*hole_centers[lobe])
    reach = blend_centers[blend] - center
    gap = blend_radii[blend] + wall
    inset = (reach.Length ** 2 + lobe_radius ** 2 - gap ** 2) / (2 * reach.Length)
    along = reach.normalized()
    aside = cq.Vector(-along.y, along.x) * math.sqrt(lobe_radius ** 2 - inset ** 2)
    meeting = [center + along * inset + aside,
               center + along * inset - aside]
    sharp_corners.append(min(meeting, key=lambda point: (point - middle).Length))

shells = []
for lobe, grow, lift in ((lobe_radius, 0.0, 0.0), (lobe_radius - wall, wall, base_height)):
    touching = []
    for i, blend_center in enumerate(blend_centers):
        for lobe_center in (lobe_centers[i], lobe_centers[(i + 1) % 3]):
            corner = cq.Vector(*lobe_center)
            touching.append(corner + (blend_center - corner).normalized() * lobe)

    shell = (cq.Workplane("XY")
             .polyline([(point.x, point.y) for point in touching])
             .close()
             .extrude(height - lift))

    for lobe_center in lobe_centers:
        shell = shell.union(cq.Workplane("XY")
                            .center(*lobe_center)
                            .circle(lobe)
                            .extrude(height - lift))

    for blend_center, blend_radius in zip(blend_centers, blend_radii):
        shell = shell.cut(cq.Workplane("XY")
                          .center(blend_center.x, blend_center.y)
                          .circle(blend_radius + grow)
                          .extrude(height - lift))

    shells.append(shell.translate((0, 0, lift)))

body, pocket = shells

body = body.faces("<Z").edges().fillet(fillet_radius)
for x, y in hole_centers:
    body = body.cut(cq.Workplane("XY")
                    .center(x, y)
                    .circle(hole_radius)
                    .extrude(height))
body = (body
        .faces(">Z")
        .edges(cq.selectors.RadiusNthSelector(0))
        .chamfer(hole_chamfer))

for x, y in hole_centers:
    pocket = pocket.cut(cq.Workplane("XY")
                        .center(x, y)
                        .circle(lobe_radius)
                        .extrude(height))

bars = []
for (x, y), angle in ribs:
    bars.append(cq.Workplane("XY")
                .rect(overrun, rib_width)
                .extrude(height)
                .rotate((0, 0, 0), (0, 0, 1), angle)
                .translate((x, y, 0)))

spine = bars[0]
for (x, y), angle in ribs[1:]:
    across = cq.Vector(-math.sin(math.radians(angle)), math.cos(math.radians(angle)))
    outward = -1 if across.dot(middle - cq.Vector(x, y)) > 0 else 1
    beyond = (cq.Workplane("XY")
              .rect(overrun, overrun)
              .extrude(height)
              .translate((0, outward * (rib_width + overrun) / 2, 0))
              .rotate((0, 0, 0), (0, 0, 1), angle)
              .translate((x, y, 0)))
    spine = spine.cut(beyond)

pocket = (pocket
          .cut(bars[1])
          .cut(bars[2])
          .cut(spine))

solid = body
for part in pocket.solids().vals():
    walls = cq.Workplane("XY").add(part)

    rounded = []
    for edge in walls.edges("|Z").vals():
        spot = edge.Center()
        if all(math.hypot(spot.x - corner.x, spot.y - corner.y) > fillet_radius
               for corner in sharp_corners):
            rounded.append(edge)

    profile = (walls
               .newObject(rounded)
               .fillet(fillet_radius)
               .faces("<Z")
               .wires()
               .val())

    redrawn = []
    for edge in profile.Edges():
        if edge.geomType() == "LINE":
            redrawn.append(cq.Edge.makeLine(edge.startPoint(), edge.endPoint()))
        else:
            redrawn.append(cq.Edge.makeThreePointArc(edge.startPoint(),
                                                     edge.positionAt(0.5),
                                                     edge.endPoint()))

    cutter = (cq.Workplane("XY")
              .add(cq.Wire.assembleEdges(redrawn))
              .toPending()
              .extrude(height)
              .faces("<Z")
              .edges()
              .fillet(fillet_radius))
    solid = solid.cut(cutter)

solid = cq.Workplane("XY").add(solid.val().scale(scale))

show_object(solid)
