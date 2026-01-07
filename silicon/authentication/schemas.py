from ninja import Schema


class FirebaseTokenIn(Schema):
    id_token: str


class AuthUserOut(Schema):
    id: int
    first_name: str
    username: str
    email: str


class HealthCheckOut(Schema):
    status: str = "online"
    service: str
