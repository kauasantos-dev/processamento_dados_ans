from pydantic import HttpUrl, BaseModel

class UrlSchema(BaseModel):
    url: HttpUrl