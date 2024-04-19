
from typing import List, Optional, Union
import dataclasses

from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.robot_descriptions import robot_description
from pycram.enums import Arms

class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str

        @with_tree
        def perform(self) -> None:
            object = self.object_designator.bullet_world_object
            object_pose = object.get_pose()
            obj_dim = object.get_object_dimensions()
            grasp = robot_description.grasps.get_pregrasp_for_grasp(self.arm)
            grasp_pose = object_pose.copy()
            grasp_pose.pose.position.x -= 0.1
            grasp_pose.pose.position.y += grasp[0]
            grasp_pose.pose.position.z += grasp[1]
            grasp_pose.pose.orientation.x = grasp[2]
            grasp_pose.pose.orientation.y = grasp[3]
            grasp_pose.pose.orientation.z = grasp[4]
            grasp_pose.pose.orientation.w = grasp[5]
            MoveTCPMotion(grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            MoveTCPMotion(object_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
