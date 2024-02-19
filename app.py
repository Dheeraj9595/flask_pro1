from flask import Flask, render_template
from flask import jsonify, request
from db import User, engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from flask import g

app = Flask(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
users_list = []


def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    database = g.pop('db', None)
    if database is not None:
        database.close()


def create_user_serializer():
    user_id: int
    name: str


def show_user_serializer(user):
    return {"id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "created_at": user.created_date.strftime('%d-%m-%Y'),
            "time": user.created_date.strftime('%H:%M')}


@app.route('/create-user/', methods=['POST'])
def create_user():
    user_data = request.json
    if user_data:
        user_id = user_data.get('user_id')
        username = user_data.get('username')
        users_list.extend([user_id, username])
    return {"message": "user created successfully...."}


#
@app.route('/users/', methods=['GET'])
def list_users():
    db = get_db()
    users = db.query(User).all()
    if users:
        sorted_users = sorted(users, key=lambda user: user.id, reverse=True)
        serializer = [show_user_serializer(user) for user in sorted_users]
        return jsonify({"users": serializer})
    else:
        return {"message": "Users data is empty..."}


@app.route('/search-users/', methods=['GET'])
def search_users():
    # Get the value of the 'q' query parameter
    query_param = request.args.get('q')
    if query_param:
        # Perform a partial match search on username, email, or any other fields
        users = db.query(User).filter(
            User.username.ilike(f'%{query_param}%'),
            User.email.ilike(f'%{query_param}%'))
        # Add more fields as needed

        # Serialize the result
        serialized_users = [show_user_serializer(user) for user in users]

        return jsonify({"status": 200, "results": len(serialized_users), "users": serialized_users}), 200
    else:
        return jsonify({"error": "Missing 'q' parameter"}), 400


@app.route('/', methods=['GET'])
def welcome():
    return render_template('index.html')


@app.route('/register/', methods=['POST'])
def register_user():
    global db
    data = request.json

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([first_name, last_name, username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        db = get_db()
        new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
        db.add(new_user)
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except IntegrityError:
        db.rollback()
        return jsonify({"error": "Username or email already exists"}), 400

    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
