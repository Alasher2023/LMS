"""rename due_date and add end_date

Revision ID: a3d5e6f7g8h9
Revises: 12d3e1eea61e
Create Date: 2025-08-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3d5e6f7g8h9'
down_revision: Union[str, None] = 'bd60f3fb02aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('paper', schema=None) as batch_op:
        batch_op.alter_column('due_date', new_column_name='start_date', existing_type=sa.DateTime())
        batch_op.add_column(sa.Column('end_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('paper', schema=None) as batch_op:
        batch_op.drop_column('end_date')
        batch_op.alter_column('start_date', new_column_name='due_date', existing_type=sa.DateTime())
