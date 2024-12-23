import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from auth.utils import ALGORITHM, SECRET_KEY, verify_password
from models.auth_model import TokenData
from database.schema import User
from database.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, username: str = None, email: str = None):
    if username:
        return db.query(User).filter(User.username == username).first()
    if email:
        return db.query(User).filter(User.email == email).first()
    return None


def authenticate_user(db: Session, password: str, username: str = None, email: str = None):
    user = None
    if username:
        user = get_user(db, username=username)
    elif email:
        user = get_user(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logging.error("Token does not contain a username (sub).")
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError as e:
        logging.error(f"Token decoding error: {e}")
        raise credentials_exception
    user = None
    if check_if_username_is_email(token_data.username):
        user = get_user(db, email=token_data.username)
    else:
        user = get_user(db, username=token_data.username)
    if user is None:
        logging.error(f"No user found with username: {token_data.username}")
        raise credentials_exception
    return user


def check_if_username_is_email(username):
    try:
        if "@" in username:
            return True
        return False
    except Exception as e:
        return False
