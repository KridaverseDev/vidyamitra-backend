# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).


python_sources(
    name="lib",
    dependencies=[
        "silicon",
        "//:requirements#django",
        "//:requirements#boto3",
        "//:requirements#django-storages",
        "//:requirements#django-cors-headers",
        "//:requirements#django-stubs-ext",
        "//:requirements#psycopg",
        "//:requirements#django-debug-toolbar",
        "//:requirements#django-ninja-extra",
        "//:requirements#loguru",
        "//:requirements#django-markdownfield",
        "//:requirements#python-pptx",
        "//:requirements#langchain-community",
        "//:requirements#langchain-openai",
        "//:requirements#langchain-core",
        "//:requirements#langchain-google-genai",
        "//:requirements#langchain-pinecone",
        "//:requirements#moodlepy",
        "//:requirements#moodlexport",
        "//:requirements#docx2txt",
        "//:requirements#python-docx",
        "//:requirements#mdutils",            
        "//:requirements#pydantic-core",            
    ],
    run_goal_use_sandbox=False
)

pex_binary(
    name="gunicorn",
    entry_point="gunicorn.py",
    dependencies=[
        ":lib","silicon/templates"
    ],
    restartable=True,
)

pex_binary(
    name="manage",
    entry_point="manage.py",
    dependencies=[":lib","silicon/templates"],
    # layout="packed",
    restartable=True,

)

