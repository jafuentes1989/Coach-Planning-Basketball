from app import create_app, db
from app.models import Sesion, Ejercicio


app = create_app()


def recalcular_duraciones():
    with app.app_context():
        sesiones = Sesion.query.all()
        actualizadas = 0

        for sesion in sesiones:
            # Si no tiene ejercicios_ids:
            # - si la duración es None, dejamos 0
            # - si ya tiene un valor, no lo tocamos
            if not sesion.ejercicios_ids:
                if sesion.duracion is None:
                    sesion.duracion = 0
                    actualizadas += 1
                continue

            # Parsear IDs de ejercicios desde la cadena "1,2, 3"
            ids = []
            for parte in sesion.ejercicios_ids.split(','):
                parte = parte.strip()
                if parte.isdigit():
                    ids.append(int(parte))

            if not ids:
                # No hay IDs válidos; si duración es None la ponemos a 0
                if sesion.duracion is None:
                    sesion.duracion = 0
                    actualizadas += 1
                continue

            # Obtener ejercicios y sumar sus duraciones
            ejercicios = Ejercicio.query.filter(Ejercicio.id.in_(ids)).all()
            duracion_total = sum((e.duracion or 0) for e in ejercicios)

            sesion.duracion = duracion_total
            actualizadas += 1

        db.session.commit()
        print(f"Sesiones actualizadas: {actualizadas}")


if __name__ == "__main__":
    recalcular_duraciones()
