from collections.abc import Callable

from core.security import verify_token
from fastapi import HTTPException, Request
from fastapi.routing import APIRoute
from models import Account, Permission, role_permission

# [수정] app. 접두사 제거 (현재 환경에 맞춤)
from database import SessionLocal


class RBACRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            # ---------------------------------------------------------
            # 1. [예외 처리] 보안 검사가 필요 없는 공개 URL (Whitelist)
            # ---------------------------------------------------------
            public_paths = [
                "/api/v1/auth/login",  # 로그인
                "/api/v1/account/register",  # 회원가입
                "/api/v1/account/check",  # 중복확인
                "/docs",  # Swagger UI
                "/openapi.json",  # Swagger JSON
                "/redoc",  # ReDoc
            ]

            # 정적 파일(/static)이나 공개 경로는 검사 없이 통과
            # OPTIONS 메서드(CORS Preflight)도 통과
            if (
                any(request.url.path.startswith(path) for path in public_paths)
                or request.url.path.startswith("/static")
                or request.url.path.startswith("/assets")
                or request.method == "OPTIONS"
            ):
                return await original_route_handler(request)

            # ---------------------------------------------------------
            # 2. DB 세션 생성 (Middleware 레벨이라 직접 생성)
            # ---------------------------------------------------------
            db = SessionLocal()

            try:
                # ---------------------------------------------------------
                # 3. [인증] Header에서 토큰 추출 및 검증
                # ---------------------------------------------------------
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

                token = auth_header.split(" ")[1]
                user_id = verify_token(token)  # 토큰에서 user_id 추출

                if not user_id:
                    raise HTTPException(
                        status_code=401, detail="유효하지 않은 토큰입니다."
                    )

                # 사용자 및 역할 조회
                user = db.query(Account).filter(Account.id == user_id).first()
                if not user or not user.role_id:
                    raise HTTPException(
                        status_code=403, detail="권한이 없는 사용자입니다."
                    )

                # ---------------------------------------------------------
                # 4. [인가] URL 분석하여 Resource, Action 도출
                # ---------------------------------------------------------
                resource = self._detect_resource(request.url.path)
                action = self._detect_action(request.method)

                # [보안] Resource를 찾지 못한 경우 -> "무조건 차단" (Fail Close)
                if resource == "unknown":
                    print(
                        f"[Security Warning] Unknown Resource Access Attempt: {request.url.path}"
                    )
                    raise HTTPException(
                        status_code=403, detail="접근 권한이 없는 리소스입니다."
                    )

                # ---------------------------------------------------------
                # 5. [권한 검사] DB 조회
                # "이 유저의 Role이 해당 Resource에 대해 Action 권한이 있는가?"
                # ---------------------------------------------------------
                has_permission = (
                    db.query(role_permission)
                    .join(
                        Permission, role_permission.c.permission_id == Permission.id
                    )  # [핵심 수정] .c 사용
                    .filter(
                        role_permission.c.role_id
                        == user.role_id,  # [핵심 수정] .c 사용
                        Permission.resource == resource,
                        Permission.action == action,
                    )
                    .first()
                )

                if not has_permission:
                    print(
                        f"[Access Denied] User: {user.id}, Role: {user.role_id}, Target: {resource}:{action}"
                    )
                    raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

            except HTTPException as he:
                raise he
            except Exception as e:
                print(f"Security Error: {str(e)}")
                raise HTTPException(status_code=401, detail="인증 처리에 실패했습니다.")
            finally:
                db.close()

            # 6. 통과 시 원래 함수 실행
            return await original_route_handler(request)

        return custom_route_handler

    def _detect_resource(self, path: str) -> str:
        """URL 경로에서 Resource 이름 추출 (프로젝트 규칙 반영)"""
        parts = path.strip("/").split("/")

        # 예: /api/v1/quotation/machine -> machine
        if "quotation" in parts:
            if "machine" in parts:
                return "machine"
            if "general" in parts:
                return "general"
            return "quotation"  # 견적서 공통

        # 예: /api/v1/parts -> parts
        if "parts" in parts:
            return "parts"
        if "maker" in parts:
            return "maker"
        if "account" in parts:
            return "account"

        return "unknown"

    def _detect_action(self, method: str) -> str:
        """HTTP Method를 Action으로 변환"""
        method_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "DELETE": "delete",
        }
        return method_map.get(method, "read")
