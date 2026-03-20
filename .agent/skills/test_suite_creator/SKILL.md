---
name: 테스트작성기
description: Generates Django unit tests for models, views, and forms to ensure platform stability.
---

# Test Suite Creator Skill

Testing is crucial for a stable platform, but writing boilerplate tests can be time-consuming. This skill helps automate the creation of a solid foundation of unit tests.

## Instructions

When the user asks to "write tests for X" or "generate a test suite":

1.  **Identify the Target**:
    - Ask the user which app or specific module (e.g., `materials.models`, `formulations.views`) needs testing.
    - Review the target code to understand its models, logic, and expected behavior.

2.  **Generate `tests.py` (or test directory structure)**:
    - If the app is small, write tests in `[app_name]/tests.py`.
    - If the app is large, suggest creating a `tests/` directory with `__init__.py`, `test_models.py`, `test_views.py`, etc.

3.  **Model Tests**:
    - Write tests for string representations (`__str__`).
    - Write tests for custom methods or properties.
    - Write tests for data integrity (e.g., ensuring a Material cannot be saved without a name).

4.  **View Tests**:
    - Use Django's `Client` or `RequestFactory`.
    - Test that pages load successfully (HTTP 200).
    - Test that the correct templates are used.
    - Test context data (e.g., ensuring "ListViews" return the correct queryset).
    - **Crucial**: Test authentication/permission requirements (e.g., ensuring anonymous users are redirected to login).

5.  **Form Tests**:
    - Test valid data submission.
    - Test invalid data validation (e.g., missing required fields, incorrect formats).

6.  **Setup and Teardown**:
    - Use `setUp()` or `setUpTestData()` to create reliable fixture data for the tests.

7.  **Output**:
    - Provide the generated code to the user. Explain how to run the specific tests (e.g., `python manage.py test materials`).
