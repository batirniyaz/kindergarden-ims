import datetime
from typing import List, Dict, Any, Optional

from app.schemas.util import TashkentBaseModel


class UnifiedLogResponse(TashkentBaseModel):
    total_count: int
    items: List[Dict[str, Any]]


class LoginInfoLog(TashkentBaseModel):
    id: int
    user_id: int
    email: str
    phone: str
    username: str
    login_at: datetime.datetime
    log_type: str = "login_info"


class ActivityLog(TashkentBaseModel):
    id: int
    user_id: int
    phone: str
    email: str
    username: str
    role: str
    query: str
    method: str
    path: str
    status_code: int
    process_time: float
    client_host: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    log_type: str = "logging"


class ChangeLog(TashkentBaseModel):
    id: int
    user_id: int
    table_name: str
    operation: str
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    log_type: str = "change_log"
