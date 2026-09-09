import math
import cadquery as cq

across_flats = 5.0
height = 2.0
thread_radius = 1.25
thread_pitch = 0.45
thread_depth = 3 * math.sqrt(3) * thread_pitch / 8
minor_radius = thread_radius - thread_depth
thread_phase = 0.040625
scale = 0.001

half_height = height / 2
outer_radius = across_flats / math.sqrt(3)
end_radius = across_flats / 2
chamfer_height = (outer_radius - end_radius) / math.sqrt(3)

hexagon = [(outer_radius * math.cos(math.radians(30 + 60 * i)),
            outer_radius * math.sin(math.radians(30 + 60 * i)))
           for i in range(6)]

body = (cq.Workplane("XY", origin=(0, 0, -half_height))
        .polyline(hexagon).close()
        .extrude(height)
        )

outside = (cq.Workplane("XZ")
           .polyline([(0, -half_height),
                      (end_radius, -half_height),
                      (outer_radius, -half_height + chamfer_height),
                      (outer_radius, half_height - chamfer_height),
                      (end_radius, half_height),
                      (0, half_height)])
           .close()
           .revolve(360, (0, 0), (0, 1))
           )

bore = (cq.Workplane("XZ")
        .polyline([(0, -half_height),
                   (thread_radius, -half_height),
                   (minor_radius, -half_height + thread_depth),
                   (minor_radius, half_height - thread_depth),
                   (thread_radius, half_height),
                   (0, half_height)])
        .close()
        .revolve(360, (0, 0), (0, 1))
        )

thread_start = thread_phase - 4 * thread_pitch
thread_length = 6.25 * thread_pitch
root_half_width = 7 * thread_pitch / 16
crest_half_width = thread_pitch / 16
cut_overlap = 0.02

helix = cq.Wire.makeHelix(thread_pitch, thread_length, thread_radius)
helix = helix.translate((0, 0, thread_start))

thread = (cq.Workplane("XZ")
          .polyline([(thread_radius + cut_overlap,
                      thread_start - root_half_width - cut_overlap / math.sqrt(3)),
                     (minor_radius, thread_start - crest_half_width),
                     (minor_radius, thread_start + crest_half_width),
                     (thread_radius + cut_overlap,
                      thread_start + root_half_width + cut_overlap / math.sqrt(3))])
          .close()
          .sweep(helix, isFrenet=True)
          )

opening = (cq.Workplane("XY", origin=(0, 0, -half_height))
           .circle(thread_radius)
           .extrude(height)
           )

solid = body.cut(opening).union(thread).intersect(outside).cut(bore)
solid = cq.Workplane("XY").add(solid.val().fix().scale(scale))

show_object(solid)
