from app.db.database import engine, Base
import app.models

print("Dropping all registered tables...")
Base.metadata.drop_all(bind=engine)
print("Creating all registered tables...")
Base.metadata.create_all(bind=engine)
print("Database reset successfully!")
