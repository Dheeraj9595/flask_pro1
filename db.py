from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, DateTime, func, String, \
    ForeignKey, Boolean

DATABASE_URL = "mysql+mysqlconnector://admin:Root*1234@localhost:3306/flask_pro1"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AbstractModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=func.now(), server_default=func.now())


class User(AbstractModel):
    __tablename__ = "user"
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(200), index=True)
    todos = relationship("Todo", back_populates="user")

    def __repr__(self):
        return '<User %r' % self.username


class Todo(AbstractModel):
    __tablename__ = "todos"
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('user.id'))  # Assuming you have a 'users' table

    # Define a relationship with the User model (assuming you have a User model)
    user = relationship("User", back_populates="todos")
