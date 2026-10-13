from typing import Callable
import importlib

#TODO: Refractor to use a dictionary of dictionaries instead of just single key value pairs. Use dictionaries of dictionaries so that Readers and Writers can be called distinctly and seperately without having to create additional logic.

class Registry:
    #string cleaning method
    @staticmethod
    def _normalize(key: str) -> str:
        return key.strip().lower().lstrip(".")
    
#initializes the registry lookup table and after cleaning key value pairs through a normalize function
    def __init__(self, mapping: dict[str, str], base_class: type) -> None:
        self._mapping = {self._normalize(s): c for s, c in mapping.items()}
        self._base_class = base_class

    

    #returns available keys
    def available(self) -> list[str]:
        return sorted(self._mapping)        

    # creates an object through passing in an import string to call up the module path and module's class and then
    # creating a new object from that class
    def create_class(self, key: str):
        normalized = self._normalize(key)
        if normalized not in self._mapping:
            raise ValueError(
                f"Unknown option '{key}'. Choose from: {', '.join(self.available())}")
        
        target = self._mapping[normalized]
        module_path, _, class_name = target.rpartition(".")
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load '{target}': {e}") from e

        if not (isinstance(cls, type) and issubclass(cls, self._base_class)):
            raise TypeError(f"'{target}' is not a subclass of {self._base_class.__name__}")

        return cls()

        