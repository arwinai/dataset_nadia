import math
import cadquery as cq

outer_radius = 38.1
disc_half_thickness = 5.55625

groove_root_radius = 31.75
groove_fillet_radius = 2.38125
groove_half_width = 4.445

shoulder_radius = 15.875
shoulder_recess_depth = 0.0635
hub_radius = 9.525
hub_recess_depth = 0.619125
bore_radius = 6.35

boss_radius = 25.4
boss_length = 44.45
boss_thickness = 12.7
scale = 0.001


shoulder_half_thickness = disc_half_thickness - shoulder_recess_depth
hub_half_thickness = disc_half_thickness - hub_recess_depth

groove_center_radius = groove_root_radius + groove_fillet_radius
mouth_distance = math.hypot(outer_radius - groove_center_radius, groove_half_width)
flank_angle = (math.atan2(groove_half_width, outer_radius - groove_center_radius)
               - math.asin(groove_fillet_radius / mouth_distance))
tangent_radius = groove_center_radius - groove_fillet_radius * math.sin(flank_angle)
tangent_height = groove_fillet_radius * math.cos(flank_angle)

upper_profile = [(bore_radius, hub_half_thickness),
                 (hub_radius, hub_half_thickness),
                 (hub_radius, shoulder_half_thickness),
                 (shoulder_radius, shoulder_half_thickness),
                 (shoulder_radius, disc_half_thickness),
                 (outer_radius, disc_half_thickness),
                 (outer_radius, groove_half_width),
                 (tangent_radius, tangent_height)]
lower_profile = [(radius, -height) for radius, height in upper_profile]
return_profile = list(reversed(upper_profile[:-1]))

boss = (cq.Workplane("XY", origin=(0, 0, disc_half_thickness))
        .moveTo(boss_radius, 0)
        .lineTo(boss_radius, boss_length)
        .lineTo(-boss_radius, boss_length)
        .lineTo(-boss_radius, 0)
        .threePointArc((0, -boss_radius), (boss_radius, 0))
        .close()
        .extrude(boss_thickness)
        )

solid = (cq.Workplane("XZ")
         .polyline(lower_profile)
         .threePointArc((groove_root_radius, 0), upper_profile[-1])
         .polyline(return_profile, includeCurrent=True)
         .close()
         .revolve(360, (0, 0), (0, 1))
         .union(boss)
         .union(boss.mirror("XY"))
         )
solid = cq.Workplane("XY").add(solid.val().scale(scale))

show_object(solid)
