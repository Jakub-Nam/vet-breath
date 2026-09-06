"""Self-service account deletion.

The schema's foreign keys carry no ON DELETE CASCADE, so dependents are removed
explicitly — children before parents. A vet deleting their account also removes
every client they supervise and all of that client's dogs, readings, and notes.
"""

from sqlmodel import Session, col, select

from app.models.dog import Dog
from app.models.note import Note
from app.models.owner import Owner
from app.models.reading import Reading
from app.models.vet import Vet


def delete_account(session: Session, user_id: int, role: str) -> None:
    """Delete the given user's own account and everything that depends on it."""
    if role == "vet":
        _delete_vet(session, user_id)
    else:
        _delete_owner(session, user_id)
    session.commit()


def _delete_owner(session: Session, owner_id: int) -> None:
    dogs = session.exec(select(Dog).where(Dog.owner_id == owner_id)).all()
    dog_ids = [dog.id for dog in dogs]
    if dog_ids:
        for reading in session.exec(select(Reading).where(col(Reading.dog_id).in_(dog_ids))).all():
            session.delete(reading)
        for note in session.exec(select(Note).where(col(Note.dog_id).in_(dog_ids))).all():
            session.delete(note)
    for dog in dogs:
        session.delete(dog)
    owner = session.get(Owner, owner_id)
    if owner is not None:
        session.delete(owner)


def _delete_vet(session: Session, vet_id: int) -> None:
    owners = session.exec(select(Owner).where(Owner.supervising_vet_id == vet_id)).all()
    for owner in owners:
        _delete_owner(session, owner.id)
    # Notes the vet authored live on their clients' dogs (already removed above);
    # this sweep is a defensive catch for any that outlived their dog.
    for note in session.exec(select(Note).where(Note.vet_id == vet_id)).all():
        session.delete(note)
    vet = session.get(Vet, vet_id)
    if vet is not None:
        session.delete(vet)
