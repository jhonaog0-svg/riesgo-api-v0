"""Utilidades transversales del servicio."""
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")


def con_registro(func: Callable[..., T]) -> Callable[..., T]:
    """Registra la llamada sin alterar excepciones ni metadata."""
    @wraps(func)
    def envoltura(*args, **kwargs):
        print(f"[registro] {func.__name__}")
        return func(*args, **kwargs)

    return envoltura
