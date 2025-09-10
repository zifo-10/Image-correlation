from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError, DataError, SQLAlchemyError
from ..exceptions.custom_exceptions import DatabaseException
from functools import wraps


def handle_db_exceptions(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            raise DatabaseException(
                status_code=400,
                detail="Integrity constraint violated",
                additional_info={"original_error": str(e.orig)}
            ) from e
        except OperationalError as e:
            raise DatabaseException(
                status_code=500,
                detail="Operational error (DB unavailable)",
                additional_info={"original_error": str(e.orig)}
            ) from e
        except ProgrammingError as e:
            raise DatabaseException(
                status_code=500,
                detail="Invalid SQL command",
                additional_info={"original_error": str(e.orig)}
            ) from e
        except DataError as e:
            raise DatabaseException(
                status_code=500,
                detail="Invalid data input",
                additional_info={"original_error": str(e.orig)}
            ) from e
        except SQLAlchemyError as e:
            raise DatabaseException(
                status_code=500,
                detail="Unexpected database error",
                additional_info={"original_error": str(e)}
            ) from e
        except Exception as e:
            raise DatabaseException(
                status_code=500,
                detail="Unexpected repository error",
                additional_info={"original_error": str(e)}
            ) from e

    return async_wrapper
