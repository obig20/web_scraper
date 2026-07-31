"""Initial database schema.

Revision ID: 001_initial
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums and tables are created via Base.metadata.create_all in dev;
    # this migration serves as the schema reference for production deploys.
    pass


def downgrade() -> None:
    pass
