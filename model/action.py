class Action:
    DESIGNATOR_FOLDER = "./data/designators"

    def __init__(self, name: str, desc: str, designator_file: str):
        self.__name = name
        self.__desc = desc
        self.__file = designator_file

    def get_name(self) -> str:
        return self.__name

    def get_description(self) -> str:
        return self.__desc

    def get_designator(self) -> str:
        with open(f"{self.DESIGNATOR_FOLDER}/{self.__file}", 'r') as file:
            return file.read()

    def __str__(self) -> str:
        return f"{self.get_name()} - {self.get_description()}:\n{self.get_designator()}"
