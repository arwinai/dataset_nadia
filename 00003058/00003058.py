import cadquery as cq

outer_ring_outer_radius = 22.225
outer_ring_inner_radius = 17.994573
inner_ring_outer_radius = 15.342925
inner_ring_inner_radius = 9.525

flange_radius = 23.749
flange_thickness = 1.5875

half_height = 7.14375
chamfer_size = 0.714375
bore_top_chamfer = 1.984375

ball_radius = 3.175
ball_pitch_radius = 16.66875
ball_count = 16
scale = 0.001


inner_ring_bottom = -half_height - flange_thickness

outer_ring_profile = [(outer_ring_inner_radius, -half_height),
                      (flange_radius, -half_height),
                      (flange_radius, -half_height + flange_thickness),
                      (outer_ring_outer_radius, -half_height + flange_thickness),
                      (outer_ring_outer_radius, half_height - chamfer_size),
                      (outer_ring_outer_radius - chamfer_size, half_height),
                      (outer_ring_inner_radius, half_height)]

inner_ring_profile = [(inner_ring_inner_radius, inner_ring_bottom + chamfer_size),
                      (inner_ring_inner_radius, half_height - bore_top_chamfer),
                      (inner_ring_inner_radius + bore_top_chamfer, half_height),
                      (inner_ring_outer_radius, half_height),
                      (inner_ring_outer_radius, inner_ring_bottom),
                      (inner_ring_inner_radius + chamfer_size, inner_ring_bottom)]

groove = (cq.Workplane("XZ")
          .moveTo(ball_pitch_radius, 0)
          .circle(ball_radius)
          .revolve(360, (0, 0), (0, 1))
          )

outer_ring = (cq.Workplane("XZ")
              .polyline(outer_ring_profile)
              .close()
              .revolve(360, (0, 0), (0, 1))
              .cut(groove)
              )

inner_ring = (cq.Workplane("XZ")
              .polyline(inner_ring_profile)
              .close()
              .revolve(360, (0, 0), (0, 1))
              .cut(groove)
              )

balls = (cq.Workplane("XY")
         .polarArray(ball_pitch_radius, 0, 360, ball_count)
         .sphere(ball_radius)
         )

solid = cq.Workplane("XY").add(outer_ring).add(inner_ring).add(balls)
solid = cq.Workplane("XY").add(cq.Compound.makeCompound(solid.vals()).scale(scale))

show_object(solid)
