from pydantic import BaseModel


class LoginRequest(BaseModel):
    id: str
    pwd: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str  # 프론트엔드 환영 메시지용
    role: str  # 프론트엔드 메뉴 제어용
