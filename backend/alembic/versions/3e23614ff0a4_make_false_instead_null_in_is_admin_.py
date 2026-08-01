"""make false instead null in is_admin column

Revision ID: 3e23614ff0a4
Revises: b67f33cccff7
Create Date: 2026-08-01 10:09:25.463454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e23614ff0a4'
down_revision: Union[str, Sequence[str], None] = 'b67f33cccff7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Устанавливаем false для всех существующих записей
    op.execute("UPDATE users SET is_admin = false WHERE is_admin IS NULL")
    # Делаем поле NOT NULL
    op.alter_column('users', 'is_admin', nullable=False, server_default='false')

def downgrade():
    op.alter_column('users', 'is_admin', nullable=True)
    op.execute("UPDATE users SET is_admin = NULL WHERE is_admin = false")
