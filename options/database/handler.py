from sqlalchemy.sql import Select, Insert, Update, Delete
from options.database.db import get_db_session
from options.log import log_factory

logger = log_factory(f"{__name__}")


def execution_handler(statement):
    try:
        session = get_db_session()
        try:
            if isinstance(statement, Select):
                result = session.execute(statement)
                return result.fetchall()

            elif isinstance(statement, Insert):
                session.execute(statement)

            elif isinstance(statement, Update):
                session.execute(statement)

            elif isinstance(statement, Delete):
                session.execute(statement)

            elif hasattr(statement, "__table__"):
                session.add(statement)

            session.commit()
            return None

        except Exception as e:
            session.rollback()
            logger.exception(f"{e.__class__.__name__}")

        finally:
            session.close()

    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
