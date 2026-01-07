python_test_utils(
    name="test_utils",
)

python_tests(
    name="tests",
    dependencies=[
        "silicon",  # For settings.py.
    ],
)

python_sources(
    dependencies=[
        "silicon/authentication/migrations",
        "//:requirements#django-ninja",
        "//:requirements#django-ninja-extra",
    ],
    
)