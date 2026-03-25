from obinus.scrapers import (
    grande_florianopolis,
    norte,
    oeste,
    serra,
    sul,
    vale_do_itajai,
)

todos = []
todos.extend(norte.todos)
todos.extend(vale_do_itajai.todos)
todos.extend(grande_florianopolis.todos)
todos.extend(oeste.todos)
todos.extend(serra.todos)
todos.extend(sul.todos)

__all__ = ["todos"]
