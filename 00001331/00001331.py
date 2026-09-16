import cadquery as cq

scale = 0.001

block_length = 50.0
block_width = 30.0
block_height = 20.0

square_hole_size = 10.0
square_edge_margin = 5.0
square_hole_x = -block_length / 2 + square_edge_margin + square_hole_size / 2
square_hole_y = block_width / 2 - square_edge_margin - square_hole_size / 2

round_hole_diameter = 10.0
round_hole_x = 4.927938
round_hole_y = -5.931069

block = (
    cq.Workplane("XY")
    .box(block_length, block_width, block_height, centered=(True, True, False))
    .faces(">Z").workplane()
    .moveTo(square_hole_x, square_hole_y)
    .rect(square_hole_size, square_hole_size)
    .cutThruAll()
    .faces(">Z").workplane()
    .moveTo(round_hole_x, round_hole_y)
    .hole(round_hole_diameter)
)

row_count = 3
column_count = 3
grid_spacing = 100.0
first_block_x = -33.394738
first_block_y = 9.924924

blocks = [
    block.val().translate((
        first_block_x + column * grid_spacing,
        first_block_y - row * grid_spacing,
        0,
    ))
    for row in range(row_count)
    for column in range(column_count)
]

solid = cq.Compound.makeCompound(blocks)
solid = cq.Workplane("XY").add(solid.scale(scale))

show_object(solid)
