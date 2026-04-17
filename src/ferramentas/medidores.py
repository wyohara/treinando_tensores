import time
from functools import wraps

def wrapper_timer(func):
    '''
    Wrapper que mede o tempo que levou para o inicio e fim da execução
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        print(f"{func.__name__} levou {time.perf_counter() - inicio:.4f}s")
        return resultado
    return wrapper