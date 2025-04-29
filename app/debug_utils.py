from app import db
from app.models import User


def reset_db():
    db.drop_all()
    db.create_all()

    users =[
        {'username': 'amy',   'email': 'amy@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'username': 'tom',   'email': 'tom@b.com',                  'pw': 'amy.pw'},
        {'username': 'yin',   'email': 'yin@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'username': 'tariq', 'email': 'trq@b.com',                  'pw': 'amy.pw'},
        {'username': 'jo',    'email': 'jo@b.com',                   'pw': 'amy.pw'}
    ]

    for u in users:
        # get the password value and remove it from the dict:
        pw = u.pop('pw')
        # create a new user object using the parameters defined by the remaining entries in the dict:
        user = User(**u)
        # set the password for the user object:
        user.set_password(pw)
        # add the newly created user object to the database session:
        db.session.add(user)

        # Add StepData and EcoPoints for each user
        for user in User.query.all():
            # Add initial StepData for the user
            initial_steps = StepData(user_id=user.id, date=datetime.utcnow(),
                                     steps=1000)  # Example: 1000 steps for initialization
            db.session.add(initial_steps)

            # Add initial EcoPoints for the user (e.g., 10 eco points)
            initial_eco_points = EcoPoints(user_id=user.id, eco_points=10, last_updated_at=datetime.utcnow())
            db.session.add(initial_eco_points)
    db.session.commit()
