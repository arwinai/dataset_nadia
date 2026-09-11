import cadquery as cq

plate_length = 15.0
plate_width = 9.998
plate_thickness = 1.65
plate_fillet = 0.5

boss_radius = 2.6
boss_length = 1.65
boss_fillet = 0.1

hole_radius = 2.4
hole_fillet = 0.1
scale = 0.001

plate = (cq.Workplane("XY")
         .box(plate_length, plate_width, plate_thickness, centered=(True, True, False))
         .edges().fillet(plate_fillet))

boss = (cq.Workplane("XZ")
        .moveTo(0, -boss_length)
        .lineTo(boss_radius - boss_fillet, -boss_length)
        .radiusArc((boss_radius, boss_fillet - boss_length), -boss_fillet)
        .lineTo(boss_radius, -boss_fillet)
        .radiusArc((boss_radius + boss_fillet, 0), boss_fillet)
        .lineTo(0, 0)
        .close()
        .revolve(360, (0, 0), (0, 1)))

hole = (cq.Workplane("XZ")
        .moveTo(0, -boss_length)
        .lineTo(hole_radius, -boss_length)
        .lineTo(hole_radius, plate_thickness - hole_fillet)
        .radiusArc((hole_radius + hole_fillet, plate_thickness), hole_fillet)
        .lineTo(0, plate_thickness)
        .close()
        .revolve(360, (0, 0), (0, 1)))

corner_x = plate_length / 2 - plate_fillet
corner_y = plate_width / 2 - plate_fillet
corner_centers = [
    (-corner_x, -corner_y, plate_fillet),
    (corner_x, -corner_y, plate_fillet),
    (corner_x, corner_y, plate_thickness - plate_fillet),
]
corner_cuts = cq.Workplane("XY").pushPoints(corner_centers).sphere(plate_fillet)

solid = plate.union(boss).cut(hole).cut(corner_cuts)
solid = solid.translate((plate_length / 2, plate_width / 2, 0))
solid = cq.Workplane("XY").add(solid.val().scale(scale))

show_object(solid)
