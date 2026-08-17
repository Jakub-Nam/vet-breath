"""SQLModel table models (persistence). Distinct from app/schemas/ (the API
boundary). Importing this package registers every table on ``SQLModel.metadata``,
which Alembic's env.py consumes as the autogenerate target — so add each new model
to the imports below when you create it.
"""

from app.models.dog import Dog
from app.models.owner import Owner
from app.models.reading import Reading
from app.models.vet import Vet

__all__ = ["Dog", "Owner", "Reading", "Vet"]
