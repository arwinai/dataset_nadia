import cadquery as cq

outer_ring_outer_radius = 0.0111125
outer_ring_inner_radius = 0.008635
inner_ring_outer_radius = 0.0072375
inner_ring_inner_radius = 0.0047625

half_height = 0.003175
chamfer_size = 0.0003175
bore_top_chamfer = 0.0008

ball_radius = 0.0015875
ball_pitch_radius = 0.0079375
ball_count = 14

groove = (cq.Workplane("XZ")
          .moveTo(ball_pitch_radius, 0)
          .circle(ball_radius)
          .revolve()
          )

outer_ring = (cq.Workplane("XY")
              .circle(outer_ring_outer_radius)
              .circle(outer_ring_inner_radius)
              .extrude(half_height, both=True)
              .edges(cq.selectors.RadiusNthSelector(-1))
              .chamfer(chamfer_size)
              .cut(groove)
              )

inner_ring = (cq.Workplane("XY")
                .circle(inner_ring_outer_radius)
                .circle(inner_ring_inner_radius)
                .extrude(half_height, both=True)
                .faces(">Z")
                .faces(">Z")
                .edges(cq.selectors.RadiusNthSelector(0))
                .chamfer(bore_top_chamfer)
                .faces("<Z")
                .edges(cq.selectors.RadiusNthSelector(0))
                .chamfer(chamfer_size)
                .cut(groove)
                )

balls = (cq.Workplane("XY")
         .polarArray(ball_pitch_radius, 360 / (2 * ball_count), 360, ball_count)
         .sphere(ball_radius)
         )

solid = cq.Workplane("XY").add(outer_ring).add(inner_ring).add(balls)

show_object(cq.Compound.makeCompound(solid))