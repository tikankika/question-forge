# Q006 Country Capitals
^question Q006
^type match
^identifier MA_Q001
^title Country Capitals
^points 3
^labels #Geography #Capitals #Analyze #Medium

@field: question_text
Match each country with its capital city.
@end_field

@field: match_config
^Randomize all
^Shuffle Yes
^Max_associations 4
@end_field

@field: pairs
^Prompt Match the countries to their capitals:
1. Sweden -> Stockholm
2. Norway -> Oslo
3. Denmark -> Copenhagen
@end_field

@field: distractors
- Helsinki
- Reykjavik
@end_field

@field: scoring
^Partial_credit Yes
^Points_per_correct_pair 1
^Points_each_wrong 0
^Points_minimum 0
@end_field

@field: feedback

@@field: general_feedback
Sweden-Stockholm, Norway-Oslo, Denmark-Copenhagen.
@@end_field

@@field: correct_feedback
All matches correct!
@@end_field

@@field: incorrect_feedback
Some matches are incorrect.
@@end_field

@@field: partial_feedback
Some matches are correct.
@@end_field

@@field: unanswered_feedback
Please match all items.
@@end_field

@end_field
