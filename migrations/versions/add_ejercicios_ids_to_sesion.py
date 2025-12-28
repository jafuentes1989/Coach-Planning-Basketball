"""add_ejercicios_ids_to_sesion

Revision ID: add_ejercicios_ids_to_sesion
Revises: add_confidencial_to_models
Create Date: 2025-12-28 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ejercicios_ids_to_sesion'
down_revision = 'add_confidencial_to_models'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('sesion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ejercicios_ids', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('sesion', schema=None) as batch_op:
        batch_op.drop_column('ejercicios_ids')
