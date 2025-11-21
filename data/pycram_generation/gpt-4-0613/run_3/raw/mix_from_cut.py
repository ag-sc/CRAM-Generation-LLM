
import dataclasses
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.bullet_world import BulletWorld
from pycram.designators.motion_designator import MoveTCPMotion
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.pose import Pose
from typing import List, Optional, Union

class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        def perform(self) -> None:
            self.object_at_execution = self.object_bowl_designator.data_copy()
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            object_bowl = self.object_bowl_designator.bullet_world_object
            oTm = object_bowl.get_pose()
            object_bowl_pose = object_bowl.local_transformer.transform_to_object_frame(oTm, object_bowl)
            ori = multiply_quaternions([object_bowl_pose.orientation.x, object_bowl_pose.orientation.y, object_bowl_pose.orientation.z, object_bowl_pose.orientation.w], grasp)
            adjusted_bowl_pose = object_bowl_pose.copy()
            adjusted_bowl_pose.orientation.x = ori[0]
            adjusted_bowl_pose.orientation.y = ori[1]
            adjusted_bowl_pose.orientation.z = ori[2]
            adjusted_bowl_pose.orientation.w = ori[3]
            MoveTCPMotion(adjusted_bowl_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
