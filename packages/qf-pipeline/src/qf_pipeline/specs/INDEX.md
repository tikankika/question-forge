# TYPE REQUIREMENTS INDEX

**Version:** 1.0  
**Datum:** 2026-01-07  
**Plats:** `/packages/qf-pipeline/src/qf_pipeline/specs/`

---

## TILLGÄNGLIGA SPECS

| Fil | Typ | Inspera Type | Status |
|-----|-----|--------------|--------|
| `multiple_choice_single.yaml` | Flerval (ett svar) | multipleChoice | ✅ Klar |
| `multiple_response.yaml` | Flerval (flera svar) | multipleResponse | ✅ Klar |
| `text_entry.yaml` | Fyll i lucka | textEntryInteraction | ✅ Klar |
| `inline_choice.yaml` | Dropdown | inlineChoiceInteraction | ✅ Klar |
| `match.yaml` | Matchning | matchInteraction | ✅ Klar |

---

## ATT IMPLEMENTERA (Prioritet 2)

| Fil | Typ | Inspera Type | Status |
|-----|-----|--------------|--------|
| `true_false.yaml` | Sant/Falskt | trueFalse | ⏳ TODO |
| `text_area.yaml` | Essä/Fritext | extendedText | ⏳ TODO |
| `audio_record.yaml` | Ljudinspelning | audioRecord | ⏳ TODO |
| `hotspot.yaml` | Klicka på bild | hotspotInteraction | ⏳ TODO |
| `graphicgapmatch.yaml` | Dra till bild | graphicGapMatch | ⏳ TODO |
| `text_entry_graphic.yaml` | Text på bild | textEntryGraphic | ⏳ TODO |
| `text_entry_math.yaml` | Matematiskt svar | textEntryMath | ⏳ TODO |
| `text_entry_numeric.yaml` | Numeriskt svar | textEntryNumeric | ⏳ TODO |
| `gapmatch.yaml` | Dra och släpp text | gapMatchInteraction | ⏳ TODO |
| `composite_editor.yaml` | Komplex fråga | compositeEditor | ⏳ TODO |
| `nativehtml.yaml` | HTML-fråga | nativeHtml | ⏳ TODO |
| `essay.yaml` | Manuell bedömning | essay | ⏳ TODO |

---

## SPEC STRUKTUR

Varje spec innehåller:

```yaml
# IDENTIFIKATION
name: "Svenska namn"
name_en: "English name"
code: "type_code"
inspera_type: "insperaTypeName"
description: "Beskrivning av frågetypen"

# KRAV
required_metadata:     # ^question, ^type, ^identifier, etc.
optional_metadata:     # ^title, ^shuffle, etc.
required_fields:       # question_text, options, answer, feedback
optional_fields:       # scoring, option_feedback, etc.

# FEL OCH FIXAR
common_issues:         # Vanliga problem med detect/fix
  - id: "issue_id"
    severity: "critical|warning|info"
    detect: "hur hitta problemet"
    message: "meddelande till användaren"
    auto_fix: true|false
    ask_user: "fråga om input behövs"
    transform: {old: new}  # för automatisk fix

# EXEMPEL
complete_example: |    # Complete QFMD example
  # Q001 ...
```

---

## ANVÄNDNING

### I Step 1 (Guided Build):

```python
from qf_pipeline.specs import load_spec

# Ladda spec för frågetyp
spec = load_spec("multiple_choice_single")

# Jämför fråga mot spec
issues = compare_to_spec(question, spec)

# För varje issue:
for issue in issues:
    if issue.auto_fix:
        # Föreslå automatisk fix
        suggestion = apply_transform(question, issue.transform)
    else:
        # Fråga användaren
        user_input = ask_user(issue.ask_user)
```

### I Step 2 (Validate):

```python
# Validate that all required_metadata and required_fields are present
validation_result = validate_against_spec(question, spec)
```

---

## NEXT STEPS

1. ✅ Create specs for the 5 most common types
2. ⏳ Implement the `load_spec()` function
3. ⏳ Implement the `compare_to_spec()` function
4. ⏳ Implement the `apply_transform()` function
5. ⏳ Test against a real file (e.g. `EXAMPLE_COURSE.md`)
6. ⏳ Create specs for the remaining 11 types

---

*Type Requirements Index | 2026-01-07*
