# Q017 Sentence Completion
^question Q017
^type gapmatch
^identifier GM_Q001
^title Fill in the Gaps
^points 3
^labels #English #Grammar #Apply #Medium

@field: question_text
Drag the words to complete the sentence correctly.
@end_field

@field: gap_config
^Reuse_alternatives No
^Token_order random
^Token_position top
^Token_size autoSize
^Type plainText
@end_field

@field: gap_items
- quickly
- slowly
- happily
- sadly
@end_field

@field: content_with_gaps
The rabbit ran {{gap_1}} through the forest and arrived home {{gap_2}}. The tortoise walked {{gap_3}} but never gave up.
@end_field

@field: pairs
1. gap_1 -> quickly
2. gap_2 -> happily
3. gap_3 -> slowly
@end_field

@field: scoring
^Points_per_correct_pair 1
^Points_each_wrong 0
^Points_minimum 0
@end_field

@field: feedback

@@field: general_feedback
Adverbs describe how actions are performed.
@@end_field

@@field: correct_feedback
All gaps filled correctly!
@@end_field

@@field: incorrect_feedback
Some gaps are filled incorrectly.
@@end_field

@@field: partial_feedback
Some gaps are correct.
@@end_field

@@field: unanswered_feedback
Please fill in all gaps.
@@end_field

@end_field
