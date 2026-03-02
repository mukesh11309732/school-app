import os
from dependency_injector import providers
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository


frappe_client = providers.Singleton(
    FrappeClient,
    frappe_url=providers.Callable(lambda: os.environ["FRAPPE_URL"]),
    api_key=providers.Callable(lambda: os.environ["FRAPPE_API_KEY"]),
    api_secret=providers.Callable(lambda: os.environ["FRAPPE_API_SECRET"])
)

student_repository = providers.Singleton(StudentRepository, client=frappe_client)

