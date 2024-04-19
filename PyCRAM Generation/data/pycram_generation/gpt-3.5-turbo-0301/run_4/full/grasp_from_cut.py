import dataclasses
import time
import math
import numpy as np
from typing import List, Optional, Union

from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription

# Pose
from pycram.pose import Pose
"""
constructor:
Pose(position: Optional[List[float]] = None, orientation: Optional[List[float]] = None, frame: str = "map", time: rospy.Time = None)
"""

# object designators
from pycram.designators.object_designator import BelieveObject, ObjectPart
"""
constructors:
BelieveObject(names: Optional[List[str]] = None, types: Optional[List[str]] = None, resolver: Optional[Callable] = None) # Description for Objects that are only believed in.
ObjectPart(names: List[str], part_of: ObjectDesignatorDescription.Object, type: Optional[str] = None, resolver: Optional[Callable] = None) # Object Designator Descriptions for Objects that are part of some other object.
"""

# location designators
from pycram.designators.location_designator import CostmapLocation
"""
constructors:
CostmapLocation(target: Union[Pose, ObjectDesignatorDescription.Object], reachable_for: Optional[ObjectDesignatorDescription.Object] = None, visible_for: Optional[ObjectDesignatorDescription.Object] = None, reachable_arm: Optional[str] = None, resolver: Optional[Callable] = None) # Uses Costmaps to create locations for complex constrains
"""

# motion designators
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
"""
constructors:
MoveTCPMotion(target: Pose, arm: Optional[str] = None, resolver: Optional[Callable] = None, allow_gripper_collision: Optional[bool] = None) # Moves the Tool center point (TCP) of the robot
MoveGripperMotion(motion: str, gripper: str, resolver: Optional[Callable] = None, allow_gripper_collision: Optional[bool] = None) # Opens or closes the gripper
"""

# action designators
from pycram.designators.action_designator import MoveTorsoAction, ParkArmsAction, PickUpAction, PlaceAction, NavigateAction
"""
constructors:
MoveTorsoAction(positions: List[float], resolver=None) # Action Designator for Moving the torso of the robot up and down
ParkArmsAction(arms: List[Arms], resolver=None) # Park the arms of the robot
PickUpAction(object_designator_description:  Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None) # Designator to let the robot pick up an object
PlaceAction(object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], target_locations: List[Pose], arms: List[str], resolver=None) # Places an Object at a position using an arm
NavigateAction(target_locations: List[Pose], resolver=None) # Navigates the Robot to a position
"""











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
