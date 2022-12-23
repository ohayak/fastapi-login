from crud.base_crud import CRUDBase
from models.media_model import ImageMedia
from schemas.media_schema import IImageMediaCreate, IImageMediaUpdate


class CRUDImageMedia(CRUDBase[ImageMedia, IImageMediaCreate, IImageMediaUpdate]):
    pass


image = CRUDImageMedia(ImageMedia)
