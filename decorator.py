from functools import wraps
from flask import request, render_template
import jwt
from secret_key import SECRET_KEY

def require_access_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access_token_cookie")
        if access_token:
            try:
                decode_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
                return func(decode_token["sub"], *args, **kwargs)  # 디코딩된 토큰을 함수에 전달하고 결과를 반환
            except jwt.ExpiredSignatureError:
                # 토큰 만료 에러 처리
                raise ValueError("토큰이 만료되었습니다. 다시 로그인해주세요")
            except jwt.InvalidTokenError:
                # 유효하지 않은 토큰 에러 처리
                raise ValueError("유효하지 않은 로그인. 다시 로그인해주세요.")
        else:
            # 토큰이 없는 경우 에러를 던집니다.
            raise ValueError("로그인한 유저만 사용 가능한 서비스 입니다.")

    return wrapper
