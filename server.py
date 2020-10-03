"""Stack exchange OAuth2 server."""
import os
from urllib.parse import urlencode

from aiohttp import ClientSession, web

sess = None
app = web.Application()
routes = web.RouteTableDef()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
API_KEY = os.environ["KEY"]
REDIRECT_URI = "https://SO-lang.scoder12.repl.co/so/callback"
OAUTH_REDIRECT = "https://stackoverflow.com/oauth?" + urlencode(
    {
        "client_id": os.environ["CLIENT_ID"],
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(["no_expiry"]),
    }
)


@routes.get("/so/auth")
async def so_auth(req: web.Request) -> web.Response:
    """Start OAuth flow by redirecting user to endpoint."""
    return web.HTTPTemporaryRedirect(OAUTH_REDIRECT)


@routes.get("/so/callback")
async def so_callback(req: web.Request) -> web.Response:
    """Handle OAuth2 callback from stack exchange API.

    Expects code in query and exchanges it for a token.
    """
    if req.query.get("error"):
        return web.Response(text="Error: " + req.query.get("error"))

    res_code = req.query.get("code")
    if not res_code:
        return web.Response(text="Error: Missing code")

    def token_error(msg: str) -> web.Response:
        return web.Response(text=f"OAuth2 Token retrieval error: {msg}", status=500)

    async with sess.post(
        "https://stackoverflow.com/oauth/access_token/json",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": res_code,
            "redirect_uri": REDIRECT_URI,
        },
    ) as r:
        if r.status != 200:
            text = await r.text()
            return token_error(text)
        data = await r.json()
        if "error_message" in data:
            return token_error(data.get("error_message"))
        if "access_token" not in data:
            return token_error("Missing token in response: " + str(data))
        return web.HTTPTemporaryRedirect(
            "/so/success?" + urlencode({"token": data["access_token"]})
        )


@routes.get("/so/success")
async def so_success(req: web.Request) -> web.Response:
    """Show key and token to user.

    Directs user to authenticate if token query parmeter missing.
    """
    if "token" not in req.query:
        return web.Response(
            text="Please <a href='/so/auth'>authenticate</a> first",
            content_type="text/html",
        )
    return web.Response(
        text=f"Success, here are your tokens\n"
        f"Keep these secret!\n"
        f"SO lang shared API Key: {API_KEY}\n"
        f"Your personal Access Token: {req.query.get('token', '???')}"
    )


@routes.get("/")
async def index(req: web.Request) -> web.Response:
    """Return 'Hello world' and a login link to /so/auth."""
    return web.Response(
        text="Hello world <a href='/so/auth'>Login</a>", content_type="text/html"
    )


app.add_routes(routes)


async def setup_session() -> web.Application:
    """App-factory to setup global ClientSession."""
    global sess
    sess = ClientSession()

    return app


if __name__ == "__main__":
    web.run_app(setup_session())
