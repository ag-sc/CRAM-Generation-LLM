
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
        pre_grasp_distance: float = 0.1

        @staticmethod
        def get_pre_grasp_pose(object_pose, pre_grasp_distance, grasp):
            pre_grasp_pose = object_pose.copy()
            pre_grasp_pose.pose.position.x -= pre_grasp_distance
            pre_grasp_pose.pose.position.y += grasp["pre_grasp"]["y"]
            pre_grasp_pose.pose.position.z += grasp["pre_grasp"]["z"]
            pre_grasp_pose.orientation.x = grasp["pre_grasp"]["orientation"][0]
            pre_grasp_pose.orientation.y = grasp["pre_grasp"]["orientation"][1]
            pre_grasp_pose.orientation.z = grasp["pre_grasp"]["orientation"][2]
            pre_grasp_pose.orientation.w = grasp["pre_grasp"]["orientation"][3]
            return pre_grasp_pose

        @staticmethod
        def get_grasp_pose(object_pose, grasp):
            grasp_pose = object_pose.copy()
            grasp_pose.pose.position.y += grasp["grasp"]["y"]
            grasp_pose.pose.position.z += grasp["grasp"]["z"]
            grasp_pose.orientation.x = grasp["grasp"]["orientation"][0]
            grasp_pose.orientation.y = grasp["grasp"]["orientation"][1]
            grasp_pose.orientation.z = grasp["grasp"]["orientation"][2]
            grasp_pose.orientation.w = grasp["grasp"]["orientation"][3]
            return grasp_pose

        @with_tree
        def perform(self):
            object = self.object_designator.bullet_world_object
            object_pose = object.get_pose()
            grasp = robot_description.grasps.get_grasp(self.arm, object.get_object_type())
            pre_grasp_pose = self.get_pre_grasp_pose(object_pose, self.pre_grasp_distance, grasp)
            grasp_pose = self.get_grasp_pose(object_pose, grasp)

            MoveGripperMotion("open", self.arm).resolve().perform()
            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()
            MoveTCPMotion(grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
