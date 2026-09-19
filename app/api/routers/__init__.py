from fastapi import APIRouter

from app.api.routers import (
    auth,
    books,
    credits,
    finance,
    gamification,
    habits,
    learning,
    nutrition,
    recurring,
    savings,
    tasks,
    water,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(finance.router)
api_router.include_router(savings.router)
api_router.include_router(credits.router)
api_router.include_router(recurring.router)
api_router.include_router(tasks.router)
api_router.include_router(habits.router)
api_router.include_router(water.router)
api_router.include_router(nutrition.router)
api_router.include_router(books.router)
api_router.include_router(learning.router)
api_router.include_router(gamification.router)
