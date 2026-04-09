# RETIRED — superseded by database/db.py.
# Re-export everything for any code that still imports from here.
from database.db import (  # noqa: F401
    get_playmode, set_playmode,
    get_authusers, add_authuser, del_authuser,
    is_cleanmode, toggle_cleanmode,
)
