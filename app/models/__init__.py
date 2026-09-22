"""
Import every model module here so that `Base.metadata` (used by Alembic's
autogenerate) sees the full schema regardless of which module happens to
be imported first.
"""

from app.models.user import User  # noqa: F401
from app.models.finance import (  # noqa: F401
    Wallet,
    TransactionCategory,
    Transaction,
    SavingsGoal,
    SavingsTransaction,
    Credit,
    CreditPayment,
    RecurringExpense,
)
from app.models.tasks import TaskItem, Habit, HabitCompletion  # noqa: F401
from app.models.water_nutrition import (  # noqa: F401
    WaterGoal,
    WaterIntake,
    WaterReminderSettings,
    FoodItem,
    NutritionGoal,
)
from app.models.books import (  # noqa: F401
    Book,
    ReadingSession,
    BookChapter,
    BookNote,
    BookSummary,
)
from app.models.learning import (  # noqa: F401
    LearningGoal,
    LearningSession,
    StudyLanguage,
    Word,
    MathExerciseRecord,
)
from app.models.workouts import (  # noqa: F401
    WorkoutPlan,
    WorkoutExercise,
    WorkoutSettings,
    WorkoutCompletion,
)
from app.models.gamification import XPRecord, Achievement, DailySummary  # noqa: F401
