import json
from dataclasses import dataclass


@dataclass
class Processing_Config:
    readers: dict{str, str}
    writers: dict{str,str}

    def __post_init__(self) -> None:
        #initializes a dictionary for readers and one for writers to pass to registry for creating the proper read/write class
        for name, pair in (("readers", self.readers), ("writers", self.writers)):
            if not isinstance(pair, dict) or not pair:
                raise ValueError(f"Config section '{name}' must be a non-empty object.")

    @classmethod

    #opens the config json file and assigns the appropriate file type class call pairs the initialized dictionaries
    def from_file(cls, path: str) -> "Processing_Config":
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Config file is not valid JSON: {e}") from e

        missing = {"readers", "writers"} - data.keys()
        if missing:
            raise ValueError(f"Config is missing sections: {missing}")

        return cls(readers=data["readers"], writers=data["writers"])




