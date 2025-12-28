"""add_tipo_sesion_to_sesion

Revision ID: add_tipo_sesion_to_sesion
Revises: add_ejercicios_ids_to_sesion
Create Date: 2025-12-28 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tipo_sesion_to_sesion'
down_revision = 'add_ejercicios_ids_to_sesion'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('sesion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_sesion', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('sesion', schema=None) as batch_op:
        batch_op.drop_column('tipo_sesion')
