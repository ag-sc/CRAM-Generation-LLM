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


class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        source_object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        container_object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            source_object_pose = self.source_object_desig.bullet_world_object.get_pose() if isinstance(self.source_object_desig, ObjectDesignatorDescription.Object) else self.source_object_desig.part_pose
            container_object_pose = self.container_object_desig.bullet_world_object.get_pose() if isinstance(self.container_object_desig, ObjectDesignatorDescription.Object) else self.container_object_desig.part_pose

            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)

            source_object_pose_in_gripper = lt.transform_pose(source_object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            container_object_pose_in_gripper = lt.transform_pose(container_object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))

            MoveTCPMotion(source_object_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()

            container_object_pose_in_gripper.pose.position.z += 0.2
            MoveTCPMotion(container_object_pose_in_gripper, self.arm).resolve().perform()

            tilt_angle = math.pi / 2
            tilt_axis = [0, 1, 0]
            tilt_quaternion = axis_angle_to_quaternion(tilt_axis, tilt_angle)
            tilted_pose = source_object_pose_in_gripper.copy()
            tilted_pose.pose.orientation = multiply_quaternions(source_object_pose_in_gripper.pose.orientation, tilt_quaternion)

            MoveTCPMotion(tilted_pose, self.arm).resolve().perform()

            time.sleep(self.duration)

            MoveTCPMotion(source_object_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm, allow_gripper_collision=True).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations

    def ground(self) -> Action:
        source_object_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_object_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_object_desig, container_object_desig, self.arms[0], self.durations[0])
