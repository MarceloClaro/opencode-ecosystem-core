"""Transaction boundary for the single daemon-owned registry repository."""

from __future__ import annotations

from sqlalchemy.engine import Connection, RootTransaction
from sqlalchemy.orm import Session

from .database import RegistryDatabase
from .repository import RegistryRepository


class SqlAlchemyUnitOfWork:
    """Own one connection, transaction, session, and repository."""

    def __init__(self, database: RegistryDatabase, *, immediate: bool = False) -> None:
        self._database = database
        self._immediate = immediate
        self._committed = False
        self._connection: Connection | None = None
        self._transaction: RootTransaction | None = None
        self.session: Session | None = None
        self.registry: RegistryRepository | None = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        connection = self._database.engine.connect()
        if self._immediate:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            transaction = connection.get_transaction()
            assert transaction is not None
        else:
            transaction = connection.begin()
        session = Session(bind=connection, expire_on_commit=False)
        self._connection = connection
        self._transaction = transaction
        self.session = session
        self.registry = RegistryRepository(session)
        return self

    def commit(self) -> None:
        if self.session is None or self._transaction is None:
            raise RuntimeError("unit of work is not active")
        self.session.flush()
        self._transaction.commit()
        self._committed = True

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        try:
            if self.session is not None and not self._committed:
                self.session.rollback()
            if self._transaction is not None and self._transaction.is_active:
                self._transaction.rollback()
        finally:
            if self.session is not None:
                self.session.close()
            if self._connection is not None:
                self._connection.close()
