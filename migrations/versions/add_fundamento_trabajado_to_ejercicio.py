"""add_fundamento_trabajado_to_ejercicio

Revision ID: add_fundamento_trabajado_to_ejercicio
Revises: 23bce1a6677b
Create Date: 2025-12-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_fundamento_trabajado_to_ejercicio'
down_revision = '23bce1a6677b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        # añadimos inicialmente como nullable para poder rellenar datos existentes
        batch_op.add_column(sa.Column('fundamento_trabajado', sa.String(length=20), nullable=True))

    # establecemos un valor por defecto para ejercicios ya existentes
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'resistencia' WHERE fundamento_trabajado IS NULL")

    # ahora, hacemos la columna NOT NULL a nivel de base de datos
    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        batch_op.alter_column('fundamento_trabajado', existing_type=sa.String(length=20), nullable=False)


def downgrade():
    with op.batch_alter_table('ejercicio', schema=None) as batch_op:
        batch_op.drop_column('fundamento_trabajado')
