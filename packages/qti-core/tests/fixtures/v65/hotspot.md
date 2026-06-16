# Q012 Cell Diagram
^question Q012
^type hotspot
^identifier HS_Q001
^title Identify Mitochondria
^points 1
^labels #Biology #Cells #Apply #Medium

@field: question_text
Click on the mitochondria in the cell diagram below.
@end_field

@field: image_config
^Background_image cell_diagram.png
^Canvas_height 400
^Enable_coloring Yes
^Shape_color #0e98f0
^Shape_opacity 0.4
@end_field

@field: hotspots
^Prompt Click on the correct area:

@@field: hotspot_1
^Shape rect
^Coords 100,150,200,250
^Correct Yes
@@end_field

@@field: hotspot_2
^Shape circle
^Coords 300,200,50
^Correct No
@@end_field

@@field: hotspot_3
^Shape rect
^Coords 50,50,150,100
^Correct No
@@end_field

@end_field

@field: scoring
^Score_correct 1
^Score_wrong 0
^Score_unanswered 0
@end_field

@field: feedback

@@field: general_feedback
Mitochondria are oval-shaped organelles with inner membrane folds called cristae.
@@end_field

@@field: correct_feedback
Correct! You identified the mitochondria.
@@end_field

@@field: incorrect_feedback
Incorrect. Look for the oval-shaped organelle with internal folds.
@@end_field

@@field: unanswered_feedback
Please click on an area of the image.
@@end_field

@end_field
