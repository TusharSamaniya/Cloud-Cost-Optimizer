from pydantic import BaseModel

class AWSCredentialsInput(BaseModel):
    access_key: str
    secret_key: str