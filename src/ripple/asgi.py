from __future__ import annotations

from starlette.responses import JSONResponse, Response

from ripple.auth import load_auth_config
from ripple.aws.profile import validate_runtime_profile
from ripple.mcp_server import app as mcp_app
from ripple.presentation.alexa_assets import load_carousel_png

CAROUSEL_PATH = "/assets/alexa/ripple-carousel-600x900.png"


class RippleASGI:
    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") == "http" and scope.get("path") == "/readyz":
            try:
                auth = load_auth_config()
                profile = validate_runtime_profile()
                structural_aws = profile.full_aws_runtime
                response = JSONResponse(
                    {
                        "status": "ready",
                        "resource": auth.resource,
                        "environment": auth.environment,
                        "runtime_mode": "aws-structural" if structural_aws else "non-aws",
                        "structural_aws_runtime": structural_aws,
                        "aws_components": ["dynamodb", "bedrock", "cloudwatch"] if structural_aws else [],
                    }
                )
            except Exception as exc:
                response = JSONResponse(
                    {"status": "not_ready", "error": str(exc)},
                    status_code=503,
                )
            await response(scope, receive, send)
            return

        if (
            scope.get("type") == "http"
            and scope.get("path") == CAROUSEL_PATH
            and scope.get("method") in {"GET", "HEAD"}
        ):
            body = load_carousel_png()
            if scope.get("method") == "HEAD":
                body = b""
            response = Response(
                content=body,
                media_type="image/png",
                headers={
                    "Cache-Control": "public, max-age=86400, immutable",
                    "X-Content-Type-Options": "nosniff",
                },
            )
            await response(scope, receive, send)
            return
        await mcp_app(scope, receive, send)


app = RippleASGI()
