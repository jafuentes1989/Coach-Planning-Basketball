"""update_fundamento_trabajado_values

Revision ID: update_fundamento_trabajado_values
Revises: add_fundamento_trabajado_to_ejercicio
Create Date: 2025-12-27 00:10:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'update_fundamento_trabajado_values'
down_revision = 'add_fundamento_trabajado_to_ejercicio'
branch_labels = None
depends_on = None


def upgrade():
    # Mapear los valores antiguos a algunos de los nuevos
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'resistencia' WHERE fundamento_trabajado = 'fisico'")
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'bote' WHERE fundamento_trabajado = 'tecnico'")
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'sistemas' WHERE fundamento_trabajado = 'tactico'")


def downgrade():
    # Volver a los valores antiguos aproximados
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'fisico' WHERE fundamento_trabajado = 'resistencia'")
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'tecnico' WHERE fundamento_trabajado = 'bote'")
    op.execute("UPDATE ejercicio SET fundamento_trabajado = 'tactico' WHERE fundamento_trabajado = 'sistemas'")
