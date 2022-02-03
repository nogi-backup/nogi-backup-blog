import json
import time
from datetime import datetime
from typing import List

import pytz


class Blog:
    _id: int
    _blog_key: str
    _member_id: int
    _title: str
    _blog_created_at: datetime
    _content: str
    _storage_type: str
    _post_paths: List[str]
    _image_paths: List[str]
    _created_at: datetime

    def __init__(self) -> None:
        self._created_at = datetime.fromtimestamp(time.time(), tz=pytz.UTC)

    @property
    def id(self) -> int:
        return self._id

    @property
    def blog_key(self) -> str:
        return self._blog_key

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def blog_created_at(self) -> datetime:
        return self._blog_created_at

    @property
    def content(self) -> str:
        return self._content

    @property
    def storage_type(self) -> str:
        return self._storage_type

    @property
    def post_paths(self) -> List[str]:
        return self._post_paths

    @property
    def image_paths(self) -> List[str]:
        return self._image_paths

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def to_dict(self) -> dict:
        return dict(
            id=self._id,
            blog_key=self._blog_key,
            member_id=self._member_id,
            title=self._title,
            blog_created_at=self._blog_created_at,
            content=self._content,
            storage_type=self._storage_type,
            post_paths=self._post_paths,
            image_paths=self._image_paths,
            created_at=self._created_at,
        )

    def to_str(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True)
