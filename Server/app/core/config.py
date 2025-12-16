import os

class Settings:
    # [보안] 실무에서는 반드시 환경변수나 .env 파일에서 가져와야 합니다.
    # 현재는 개발 편의를 위해 기본값을 넣어둡니다.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dhH%@)$#*0yhdilKDJ!)*#$)AyuodfYD)*08308740)*&D)*D7087sd087f)D&F)&03uEH")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1일 (24시간)

settings = Settings()