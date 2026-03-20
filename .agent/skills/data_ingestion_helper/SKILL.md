---
name: 데이터가져오기
description: Assists in importing existing Excel or CSV data into the Django R&D database.
---

# Data Ingestion Helper Skill

Researchers often have legacy data in Excel or CSV files. This skill helps automate the tedious process of writing scripts to parse these files and save them as Django model instances.

## Instructions

When the user asks to "import data from Excel/CSV" or "write a data ingestion script":

1.  **Understand Target Model**:
    - Ask the user which Django model(s) the data will be imported into.
    - Review the `models.py` structure of that target model to understand its fields, data types, and required relationships (Foreign Keys).

2.  **Analyze Source Data Format**:
    - Ask the user for the column headers of their Excel/CSV file, or a small sample row.
    - Map the Excel/CSV columns to the Django Model fields.

3.  **Generate Ingestion Script**:
    - Create a standalone Python script, or preferably a Django Management Command (`management/commands/import_data.py`).
    - The script should:
        - Use standard libraries like `csv` or `pandas` (if available and requested).
        - Include proper error handling (e.g., skipping empty rows, wrapping `Model.objects.create` in a `try...except` block to catch IntegrityErrors, ValidationErrors).
        - Handle Foreign Key relationships gracefully (e.g., querying for the referenced object first, or creating it if it doesn't exist optionally).
        - Print a summary of the import process (e.g., "Successfully imported 50 rows, failed 2 rows").

4.  **Provide Instructions**:
    - Explain to the user how to run the script (e.g., `python manage.py import_data path/to/file.csv`).
    - Warn them to test it on a small sample of data first.
