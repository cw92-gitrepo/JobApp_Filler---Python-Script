import importlib



class Registry:
    #initializes the registry dictionary and creates string normalizing callable
    def __init__(self, mapping: dict[str, str], base_class: type) -> None:
        self._mapping = {self._normalize(s): c for s, c in mapping.items()}
        self._base_class = base_class

    #the actual normalizing method used by callable ._mapping
    @staticmethod
    def _normalize(key: str) -> str:
        return key.strip().lower().lstrip(".")

    #returns available keys
    def available(self) -> list[str]:
        return sorted(self._mapping)

    #creates an object through passing a string as a value and returning the values key 
    def create(self, key: str):
        normalized = self._normalize(key)
        if normalized not in self._mapping:
            raise ValueError(
                f"Unknown option '{key}'. Choose from: {', '.join(self.available())}"
            )
        
    #returns the class type given a string
    def get_class(self, key: str):
        normalized = self._normalize(key)
        if normalized not in self._mapping:
            raise ValueError(
                f"Unknown option '{key}'. Choose from: {', '.join(self.available())}"
            )

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