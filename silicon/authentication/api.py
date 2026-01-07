from ninja import File, UploadedFile
from ninja_extra import ControllerBase, api_controller, route

from silicon.authentication import schemas, services


@api_controller("v1/auth/", tags=["Authentication"])
class AuthenticationAPI(ControllerBase):
    def __init__(
        self,
        auth_service: services.AuthenticationService,
    ):
        self.auth_service = auth_service

    @route.get(
        "/healthcheck/",
        url_name="auth-health-check",
        response={200: schemas.HealthCheckOut},
    )
    def healthcheck(self, request):
        return {"service": "auth-service"}

    @route.post("/login/", url_name="login", response={200: schemas.AuthUserOut})
    def login(self, request, payload: schemas.FirebaseTokenIn):
        return self.auth_service.firebase_login(payload.id_token)
