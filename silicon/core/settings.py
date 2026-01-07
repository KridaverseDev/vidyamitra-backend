"""
Django settings for vidyamitra backend.

Settings are loaded based on APP_MODE environment variable:
- local: silicon._settings.local
- dev: silicon._settings.development  
- prod: silicon._settings.production
"""

import os
import sys
from pathlib import Path

# Add project root to Python path if not already there
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

__APP_MODE__ = os.environ.get("APP_MODE", "local").lower()

if __APP_MODE__ in ("local",):
    from silicon._settings.local import *  # noqa: F403, F401
elif __APP_MODE__ in ("dev", "development"):
    from silicon._settings.development import *  # noqa: F403, F401
elif __APP_MODE__ in ("prod", "production"):
    from silicon._settings.production import *  # noqa: F403, F401
else:
    # Default to local if unknown mode
    from silicon._settings.local import *  # noqa: F403, F401

