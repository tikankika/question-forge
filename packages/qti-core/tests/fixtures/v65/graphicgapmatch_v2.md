# Q013 Cell Parts
^question Q013
^type graphicgapmatch_v2
^identifier GGM_Q001
^title Label Cell Parts
^points 3
^labels #Biology #Cells #Apply #Medium

@field: question_text
Drag the labels to the correct parts of the cell diagram.
@end_field

@field: image_config
^Background_image cell_diagram.png
^Reuse_alternatives No
^Gap_size sameSize
^Token_order random
^Token_position top
^Token_size autoSize
^Type plainText
@end_field

@field: gap_texts
- Mitochondria
- Nucleus
- Cell membrane
- Ribosome
@end_field

@field: hotspots

@@field: hotspot_1
^Shape rect
^Coords 100,150,200,250
^Correct_item Mitochondria
@@end_field

@@field: hotspot_2
^Shape rect
^Coords 250,100,350,200
^Correct_item Nucleus
@@end_field

@@field: hotspot_3
^Shape rect
^Coords 50,50,400,350
^Correct_item Cell membrane
@@end_field

@end_field

@field: scoring
^Points_per_correct_pair 1
^Points_each_wrong 0
^Points_minimum 0
@end_field

@field: feedback

@@field: general_feedback
Review cell organelle locations and functions.
@@end_field

@@field: correct_feedback
All labels placed correctly!
@@end_field

@@field: incorrect_feedback
Some labels are misplaced.
@@end_field

@@field: partial_feedback
Some labels are correct.
@@end_field

@@field: unanswered_feedback
Please drag all labels onto the diagram.
@@end_field

@end_field
