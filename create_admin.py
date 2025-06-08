from models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

admin = User(
    username="admin",
    password_hash=generate_password_hash("admin123"),
    rolle="superadmin"
)

session.add(admin)
session.commit()
print("✅ Admin wurde erstellt.")
