---
name: 다이어그램생성기
description: Generates an ER diagram and Markdown documentation from Django models.py files.
---

# ER Diagram Generator Skill

As the R&D Platform grows, the relationships between Materials, Formulations, Experiments, and other entities become complex. 
This skill helps developers and researchers quickly understand the database schema.

## Instructions

When the user asks to "generate an ER diagram" or "visualize the database structure":

1.  **Analyze `models.py` Files**:
    - Iterate through the apps in the project (e.g., `materials`, `formulations`, `experiments`, `reports`).
    - Read the `models.py` file in each app.

2.  **Extract Model Information**:
    - For each model, identify the name of the model.
    - Identify the fields, their types (e.g., `CharField`, `IntegerField`), and any specific constraints (e.g., `null=True`, `max_length=100`).
    - **Crucially**, identify relationships: `ForeignKey`, `OneToOneField`, `ManyToManyField` and note what model they point to.

3.  **Generate Mermaid Diagram Script**:
    - Construct a `mermaid` script using the `erDiagram` syntax.
    - Format relationships correctly:
        - One-to-Many: `MODEL_A ||--o{ MODEL_B : "rel_name"`
        - Many-to-Many: `MODEL_A }o--o{ MODEL_B : "rel_name"`
        - One-to-One: `MODEL_A ||--|| MODEL_B : "rel_name"`

4.  **Generate Markdown Documentation**:
    - Create a Markdown file (e.g., `ER_DIAGRAM.md` or similar appropriate name).
    - Embed the generated Mermaid script inside a code block (` ```mermaid ` ... ` ``` `).
    - Include a brief summary of the main entities and their roles.

5.  **Output**:
    - Ask the user if they'd like this saved to a file (like `docs/schema.md`) or just displayed in the chat.
