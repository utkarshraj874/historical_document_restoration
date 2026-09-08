from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import Usercreate
from app.schemas.user import UserResponse

from app.core.dependencies import get_db
from app.core.security import hash_password
from app.core.security import verify_password

from app.core.security import pwd_context
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user:Usercreate,
             db:Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail = "Email already registered "
        )

    db_user = User(
        email = user.email,
        password_hash = hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentails"
        )
    if not verify_password(
        form_data.password,
        db_user.password_hash
        ):
        raise HTTPException(
            status_code=401,
            detail = "Invalid credentails "
        )

    access_token = create_access_token(
        data = {
            "sub":db_user.email
        }
    )

    return {
        "access_token":access_token,
        "token_type":"bearer"
    }

@router.get("/me")
def read_me(
    current_user: User = Depends(
        get_current_user
        )
    ):

    print("aa gya")

    return {
        "id":current_user.id,
        "email":current_user.email
    }
