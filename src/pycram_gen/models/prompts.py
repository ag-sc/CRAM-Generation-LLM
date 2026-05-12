sys_prompt_pycram = (
    "The following Python source code describes a PyCRAM designator for the action of \'{reference_name}\', where the robot would {reference_description}\\"
    "```python\\"
    "{reference_designator}\\"
    "```")

sys_prompt_translate = (
    "The following Lisp source code describes a CRAM designator for the action of \'{action_name}\', where the robot would {cram_description}\\"
    "```lisp\\"
    "{cram_designator}\\"
    "```\\"
    "PyCRAM designators are written in Python and have the following basic structure:\\"
    "```python\\"
    "{pycram_basic_structure}\\"
    "```")

usr_prompt_pycram = (
    "Take the example and create a new designator for the action \'{target_name}\', where the robot should {target_description}."
    "Output only the designator with no additional text. Do not include comments in the code. Use only the imported libraries and designators. Use the following constructor: {target_constructor}")

usr_prompt_translate = (
    "Take the CRAM designator and convert it into a PyCRAM designator (include an implementation of the perform method) for the same action of \'{action_name}\', where the robot should {pycram_description}. "
    "Output only the designator with no additional text. Do not include comments in the code. Do not explain yourself or the code. Follow the provided basic structure and use only the imported libraries and designators. Use the following "
    "constructor: {pycram_constructor}")
