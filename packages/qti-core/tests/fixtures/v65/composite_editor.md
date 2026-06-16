# Q015 Mixed Question
^question Q015
^type composite_editor
^identifier CE_Q001
^title Geography Quiz
^points 4
^labels #Geography #Europe #Analyze #Hard

@field: question_text
Answer all parts of this geography quiz.

Part A: The capital of France is {{blank_1}}.
Part B: Select the correct continent for France: {{dropdown_1}}
Part C: France is a member of the EU: {{choice_1}}
Part D: Name a country bordering France: {{blank_2}}
@end_field

@field: responses

@@field: response_1
^Type text_entry
^Correct_Answers
- Paris
- paris
@@end_field

@@field: response_2
^Type inline_choice
^Options
- Asia
- Europe*
- Africa
- Americas
@@end_field

@@field: response_3
^Type choice
^Options
- True*
- False
@@end_field

@@field: response_4
^Type text_entry
^Correct_Answers
- Germany
- Spain
- Italy
- Belgium
- Switzerland
@@end_field

@end_field

@field: scoring
^Points_per_correct 1
^Points_minimum 0
@end_field

@field: feedback

@@field: general_feedback
France is in Western Europe, capital Paris, EU member, borders Germany, Spain, Italy, Belgium, Switzerland, Luxembourg, Monaco, Andorra.
@@end_field

@@field: correct_feedback
All parts correct!
@@end_field

@@field: incorrect_feedback
Some parts are incorrect.
@@end_field

@@field: partial_feedback
Some parts are correct.
@@end_field

@@field: unanswered_feedback
Please answer all parts.
@@end_field

@end_field
