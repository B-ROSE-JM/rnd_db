---
name: 모듈생성기
description: Autogenerates Django Model, Form, View, URL, and HTML templates for new R&D data types.
---

# CRUD Scaffolder Skill

This skill is designed to automate the repetitive boilerplate creation process when adding a new data type (like a new entity, experiment type, or resource) to the R&D database platform.

## Context
The project is a Django application tailored for R&D data management (Materials, Formulations, Experiments, Reports). 
It uses Django forms and templates (typically styled consistently with Bootstrap/Tailwind if present, or generic clean HTML structured around blocks).

## Instructions

When the user asks to "create a new CRUD module" or "use the CRUD scaffolder for X":

1.  **Gather Requirements**: 
    - Ask the user which app this belongs to (e.g., `materials`, `experiments`, or a new app).
    - Ask for the Model Name (e.g., `Equipment`).
    - Ask for the desired fields and their types (e.g., `name` (Char), `purchase_date` (Date), `is_active` (Boolean)).

2.  **Generate `models.py`**:
    - Write the Django model with the specified fields.
    - Add `__str__` method.
    - Add `get_absolute_url` if appropriate.

3.  **Generate `forms.py`**:
    - Create a `ModelForm` for the new model.
    - Ensure standard styling classes are applied to widgets if necessary.

4.  **Generate `views.py`**:
    - Create `ListView`, `CreateView`, `UpdateView`, `DeleteView`, and `DetailView` (if requested).
    - Ensure appropriate `success_url` is set.

5.  **Generate `urls.py`**:
    - Define URL patterns mapped to the created Views.

6.  **Create Templates**:
    - Create `[model_name]_list.html` and `[model_name]_form.html` in the appropriate template directory.
    - Make sure to extend the base template (`base.html` if it exists) and wrap content in standard blocks (e.g., `{% block content %}`).

7.  **Migrations**:
    - Remind the user (or execute if permitted) to run `python manage.py makemigrations` and `python manage.py migrate`.
