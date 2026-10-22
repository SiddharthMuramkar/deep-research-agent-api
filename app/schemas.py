"""The shapes of the API's request and response bodies (Pydantic).

FastAPI checks every incoming body against these models. A body that doesn't
fit is rejected with a 422 before any of our code runs.
"""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.tables import RunStatus

# 1 to 2000 characters, after trimming spaces from both ends.
QueryText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
]


class QueryRequest(BaseModel):
    query: QueryText


class QueryAccepted(BaseModel):
    run_id: uuid.UUID
    status: RunStatus


class RunStatusResponse(BaseModel):
    run_id: uuid.UUID
    status: RunStatus
    error: str | None
    created_at: datetime
    updated_at: datetime
