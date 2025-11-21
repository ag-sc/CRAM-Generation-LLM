
from typing import List, Optional, Union
import dataclasses
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.robot_descriptions import robot_description
from pycram.enums import Arms

class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectDesignatorDescription]
        arms: List[str]
        grasps: List[str]

        def perform(self) -> None:
            gripper_name = robot_description.get_tool_frame(self.arms[0])
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveTCPMotion(self.object_bowl_desig, self.arms[0]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms, self.grasps)
