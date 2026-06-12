from fastapi_users import schemas


UserRead = schemas.BaseUser[int]
UserCreate = schemas.BaseUserCreate
UserUpdate = schemas.BaseUserUpdate