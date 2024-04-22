
from typing import List, Union
import numpy as np
from pycram.designator import ActionDesignatorDescription, ObjectDesignatorDescription
from pycram.enums import Arms
from pycram.task import with_tree

class CutAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arms: List[str]
        grasps: List[str]
        techniques: List[str]
        slice_thicknesses: List[float]

        @with_tree
        def perform(self) -> None:
            object_pose = self.object_designator.get_pose()
            for arm in self.arms:
                for grasp in self.grasps:
                    for technique in self.techniques:
                        if technique == "slicing":
                            for thickness in self.slice_thicknesses:
                                # perform slicing action
                                pass
                        elif technique == "halving":
                            # perform halving action
                            pass

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms, self.grasps, self.techniques, self.slice_thicknesses)
