import math
import cadquery as cq

shaft_length = 10.0
head_height = 2.5
head_radius = 2.25
head_chamfer = 0.225

thread_radius = 1.25
thread_pitch = 0.45
thread_crest_z = 0.309375
thread_depth = 3 * math.sqrt(3) * thread_pitch / 8
root_radius = thread_radius - thread_depth
crest_half_width = thread_pitch / 16
root_half_width = 7 * thread_pitch / 16
fusion_overlap = 0.02
thread_margin = thread_pitch

tip_radial_relief = 0.254
tip_angle = 55.0
tip_radius = root_radius - tip_radial_relief

socket_across_flats = 2.0
socket_depth = 1.5
socket_sides = 6
socket_corner_radius = socket_across_flats / math.sqrt(3)
socket_rotation = 30.0
socket_entry_angle = 45.0
socket_entry_height = socket_corner_radius / math.tan(math.radians(socket_entry_angle))
mesh_tolerance = 0.001
mm_to_m = 0.001

head_bottom_z = -shaft_length - head_height
head_top_z = -shaft_length
head_end_radius = head_radius - head_chamfer

head_profile = [
    (0, head_bottom_z),
    (head_end_radius, head_bottom_z),
    (head_radius, head_bottom_z + head_chamfer),
    (head_radius, head_top_z - head_chamfer),
    (head_end_radius, head_top_z),
]

core = (cq.Workplane("XZ")
        .polyline(head_profile + [(root_radius, head_top_z),
                                  (root_radius, 0), (0, 0)])
        .close()
        .revolve(360, (0, 0), (0, 1))
        )

thread_start = thread_crest_z - math.ceil(
    (shaft_length + thread_margin + thread_crest_z) / thread_pitch
) * thread_pitch
thread_height = math.ceil((thread_margin - thread_start) / thread_pitch) * thread_pitch
root_extension = fusion_overlap / math.sqrt(3)

helix = cq.Wire.makeHelix(thread_pitch, thread_height, thread_radius)
helix = helix.translate((0, 0, thread_start))

thread_profile = [
    (root_radius - fusion_overlap, thread_start - root_half_width - root_extension),
    (thread_radius, thread_start - crest_half_width),
    (thread_radius, thread_start + crest_half_width),
    (root_radius - fusion_overlap, thread_start + root_half_width + root_extension),
]

thread = (cq.Workplane("XZ")
          .polyline(thread_profile)
          .close()
          .sweep(helix, isFrenet=True)
          )

limit_radius = head_radius + thread_margin
limit_bottom_z = head_bottom_z - thread_margin
cone_base_z = -(limit_radius - tip_radius) / math.tan(math.radians(tip_angle))

envelope = (cq.Workplane("XZ")
            .polyline([(0, limit_bottom_z),
                       (limit_radius, limit_bottom_z),
                       (limit_radius, cone_base_z),
                       (tip_radius, 0), (0, 0)])
            .close()
            .revolve(360, (0, 0), (0, 1))
            )

socket_points = [
    (socket_corner_radius * math.cos(math.radians(socket_rotation + i * 360 / socket_sides)),
     socket_corner_radius * math.sin(math.radians(socket_rotation + i * 360 / socket_sides)))
    for i in range(socket_sides)
]

socket = (cq.Workplane("XY", origin=(0, 0, head_bottom_z))
          .polyline(socket_points).close()
          .extrude(socket_depth)
          )

socket_entry = cq.Solid.makeCone(
    socket_corner_radius, 0, socket_entry_height,
    cq.Vector(0, 0, head_bottom_z), cq.Vector(0, 0, 1)
)

solid = core.union(thread).intersect(envelope).cut(socket).cut(socket_entry)
thread_planes = [
    cq.Face.makePlane(2 * head_radius, 2 * head_radius,
                      (0, 0, -i * thread_pitch), (0, 0, 1))
    for i in range(1, math.ceil(shaft_length / thread_pitch))
]
sections = solid.val().split(*thread_planes).Solids()
solid = sections[0].fuse(*sections[1:])
solid = cq.Workplane("XY").add(solid.fix().scale(mm_to_m))

solid.val().mesh(mesh_tolerance * mm_to_m)

show_object(solid)
