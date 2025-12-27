"""add_confidencial_to_models

Revision ID: add_confidencial_to_models
Revises: add_more_images_to_ejercicio
Create Date: 2025-12-27 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_confidencial_to_models'
down_revision = 'add_more_images_to_ejercicio'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confidencial', sa.Boolean(), nullable=True))

    with op.batch_alter_table('sesion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confidencial', sa.Boolean(), nullable=True))

    with op.batch_alter_table('planning', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confidencial', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('planning', schema=None) as batch_op:
        batch_op.drop_column('confidencial')

    with op.batch_alter_table('sesion', schema=None) as batch_op:
        batch_op.drop_column('confidencial')

    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        batch_op.drop_column('confidencial')
