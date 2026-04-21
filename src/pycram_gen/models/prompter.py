class Prompter:
    def __init__(self, model: str, temp=0.0):
        self._model_name = model
        self._temperature = temp

    def generate_designator(self, reference_name: str, reference_description: str,
                            reference_designator: str, target_name: str, target_description: str,
                            target_constructor: str) -> str:
        """
        Generate a designator using an LLM by providing a reference designator

        :param reference_name: The reference action's name
        :param reference_description: The reference action's description
        :param reference_designator: The full reference designator
        :param target_name: The target action's name
        :param target_description: The target action's description
        :param target_constructor: The target action's constructor
        :returns: The generated designator
        """
        pass

    def translate_cram_designator(self, action_name: str, cram_description: str, cram_designator: str,
                                  pycram_basic_structure: str, pycram_description: str, pycram_constructor: str) -> str:
        """
        Convert a CRAM designator into a PyCRAM designator using an LLM

        :param action_name: The name of the action
        :param cram_description: The action description of the CRAM designator
        :param cram_designator: The CRAM designator
        :param pycram_basic_structure: The basic structure of a PyCRAM designator
            with import statements
        :param pycram_description: The action description of the PyCRAM designator
        :param pycram_constructor: The constructor of the PyCRAM designator
        :returns: The generated PyCRAM designator
        """
        pass

    def extract_designator(self, model_answer: str) -> str:
        """
        Extracts the generated PyCRAM designator from the model's response

        :param model_answer: The model's full response (ChatCompletion object)
        :returns: The designator contained in the response, any additional
            output is removed
        :raises PrompterException: If the finish reason is not 'stop'
            (i.e., any reason apart from the default). Exception argument
            is dictionary containing exception message, finish reason,
            and generated response.
        """
        pass

    def get_model_name(self) -> str:
        return self._model_name
