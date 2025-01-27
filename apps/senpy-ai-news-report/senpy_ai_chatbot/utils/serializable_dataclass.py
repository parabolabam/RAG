import dataclasses


@dataclasses.dataclass
class SerilizableDataclass:
    def snake_to_camel(self, input: str) -> str:
        # Can swap out with more sophisticated implementation if needed
        camel_cased = "".join(x.capitalize() for x in input.lower().split("_"))
        if camel_cased:
            return camel_cased[0].lower() + camel_cased[1:]
        else:
            return camel_cased

    def to_json(self, include_null=False) -> dict:
        """Converts this to json. Assumes variables are snake cased, converts to camel case.

        Args:
            include_null (bool, optional): Whether null values are included. Defaults to False.

        Returns:
            dict: Json dictionary
        """
        return dataclasses.asdict(
            self,
            dict_factory=lambda fields: {
                self.snake_to_camel(key): value
                for (key, value) in fields
                if value is not None or include_null
            },
        )
