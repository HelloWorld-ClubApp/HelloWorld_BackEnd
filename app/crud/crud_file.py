# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from app.models.file import File

def create_file(db: Session, url: str, file_type: str, size: int, name: str):
    new_file = File(file_url=url, file_type=file_type, file_size=size, original_name=name)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file