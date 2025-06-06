"""add package fields

Revision ID: 8cbfbe3c61a2
Revises: c59c7e33a567
Create Date: 2025-06-01 20:08:44.628702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8cbfbe3c61a2'
down_revision: Union[str, None] = 'c59c7e33a567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    op.add_column('packages', sa.Column('from_address', sa.String(), nullable=True))
    op.add_column('packages', sa.Column('weight', sa.Float(), nullable=True))
    op.add_column('packages', sa.Column('price', sa.Float(), nullable=True))
    op.add_column('packages', sa.Column('urgency', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('packages', 'urgency')
    op.drop_column('packages', 'price')
    op.drop_column('packages', 'weight')
    op.drop_column('packages', 'from_address')
    op.create_table('orders',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('from_city', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('to_city', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('weight', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('urgency', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('payment_method', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='orders_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='orders_pkey')
    )
    # ### end Alembic commands ###
