"""add_more_images_to_ejercicio

Revision ID: add_more_images_to_ejercicio
Revises: update_fundamento_trabajado_values
Create Date: 2025-12-27 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_more_images_to_ejercicio'
down_revision = 'update_fundamento_trabajado_values'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        batch_op.add_column(sa.Column('imagen_url_2', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('imagen_url_3', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        batch_op.drop_column('imagen_url_2')
        batch_op.drop_column('imagen_url_3')
