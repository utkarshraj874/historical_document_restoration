from app.core.database import SessionLocal
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import  oauth2_scheme
from app.core.security import verify_access_token

from app.models.user import User
from app.core.database import SessionLocal
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_current_user(
        
        token : str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    payload = verify_access_token(token)
    print("info of user", payload)

    email = payload.get("sub")

    if email is None:

        raise HTTPException(
            status_code=401,
            detail=" user not found "
        )
    user = db.query(User).filter(
        User.email == email
    ).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail=" user not found "
        )
    return user