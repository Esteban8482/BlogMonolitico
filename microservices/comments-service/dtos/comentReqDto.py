from dataclasses import dataclass


@dataclass
class CommentReqDto:
    post_id: str
    username: str
    content: str

    @classmethod
    def from_json(cls, payload: dict):
        if not isinstance(payload, dict):
            raise ValueError("Invalid JSON body")
        
        post_id = str(payload.get("post_id", "")).strip()
        content = str(payload.get("content", "")).strip()
        username = str(payload.get("username", "")).strip()
        
        if not post_id:
            raise ValueError("post_id is required")
        if not content:
            raise ValueError("content is required")
        if not username:
            raise ValueError("username is required")
        if len(content) > 5000:
            raise ValueError("content too long (max 5000)")
        
        return cls(post_id=post_id, content=content, username=username)