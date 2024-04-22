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


class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            tool_desig = ObjectPart(names=["mixing_tool"], part_of=robot_desig.resolve(), type="Tool")
            bowl_pose_desig = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)

            bowl_pose = next(bowl_pose_desig, None)
            if not bowl_pose:
                raise ObjectUndeliverable(f"Cannot find a pose to perform mixing at the bowl: {self.object_bowl_designator}")

            NavigateAction([bowl_pose.pose]).resolve().perform()
            PickUpAction.Action(tool_desig, [self.arm], [self.grasp]).perform()

            mixing_motion = self.generate_mixing_motion(bowl_pose.pose)
            for pose in mixing_motion:
                MoveTCPMotion(target=pose, arm=self.arm).resolve().perform()

            PlaceAction.Action(tool_desig, [bowl_pose.pose], [self.arm]).perform()

        def generate_mixing_motion(self, bowl_pose: Pose) -> List[Pose]:
            mixing_poses = []
            radius_increment = 0.01
            angle_increment = math.pi / 8
            max_radius = 0.1
            current_radius = 0.0
            current_angle = 0.0

            while current_radius < max_radius:
                x_offset = current_radius * math.cos(current_angle)
                y_offset = current_radius * math.sin(current_angle)
                position = [bowl_pose.position[0] + x_offset, bowl_pose.position[1] + y_offset, bowl_pose.position[2]]
                orientation = bowl_pose.orientation
                mixing_poses.append(Pose(position, orientation, bowl_pose.frame))

                current_angle += angle_increment
                if current_angle >= 2 * math.pi:
                    current_angle -= 2 * math.pi
                    current_radius += radius_increment

            return mixing_poses

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        obj_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_bowl_desig, self.arms[0], self.grasps[0])
