import os
import secrets
from urllib.parse import urlencode

from dotenv import load_dotenv
from starlette.responses import RedirectResponse

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPES = " ".join([
    "user-read-private",
    "user-read-email",
    "playlist-read-private"
])

async def login():

    state = secrets.token_hex(16)

    params = urlencode({
        "response_type": "code",
        "client_id": SPOTIFY_CLIENT_ID,
        "scope": SCOPES,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "state": state
    })

    return RedirectResponse(f"https://accounts.spotify.com/authorize?{params}")