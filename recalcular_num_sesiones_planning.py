from app import create_app, db
from app.models import Planning, Sesion


app = create_app()


def recalcular_num_sesiones():
    with app.app_context():
        plannings = Planning.query.all()
        actualizadas = 0

        for planning in plannings:
            if planning.sesiones_ids:
                ids = []
                for parte in planning.sesiones_ids.split(','):
                    parte = parte.strip()
                    if parte.isdigit():
                        valor = int(parte)
                        if valor not in ids:
                            ids.append(valor)

                if ids:
                    sesiones = Sesion.query.filter(Sesion.id.in_(ids)).all()
                    nuevo_num = len(sesiones)
                else:
                    nuevo_num = 0
            else:
                nuevo_num = 0

            if planning.num_sesiones != nuevo_num:
                planning.num_sesiones = nuevo_num
                actualizadas += 1

        db.session.commit()
        print(f"Plannings actualizadas: {actualizadas}")


if __name__ == "__main__":
    recalcular_num_sesiones()
