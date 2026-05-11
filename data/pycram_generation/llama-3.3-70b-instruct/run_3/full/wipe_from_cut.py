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

class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str
        gap: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth_designator.data_copy()
            cloth = self.object_cloth_designator.bullet_world_object
            for location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                oTm = location
                object_pose = oTm
                num_strips = int(length // 0.1)
                strip_poses = []
                for i in range(num_strips):
                    tmp_pose = object_pose.copy()
                    tmp_pose.pose.position.x = object_pose.pose.position.x + (i * 0.1)
                    sTm = tmp_pose
                    strip_poses.append(sTm)
                for strip_pose in strip_poses:
                    ori = [0, 0, 0, 1]
                    adjusted_strip_pose = strip_pose.copy()
                    adjusted_strip_pose.orientation.x = ori[0]
                    adjusted_strip_pose.orientation.y = ori[1]
                    adjusted_strip_pose.orientation.z = ori[2]
                    adjusted_strip_pose.orientation.w = ori[3]
                    lift_pose = adjusted_strip_pose.copy()
                    lift_pose.pose.position.z += 0.01
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                    MoveTCPMotion(adjusted_strip_pose, self.arm).resolve().perform()
                    lift_pose.pose.position.x += width
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()

        def to_sql(self) -> None:
            return None

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            return None

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super(WipeAction, self).__init__(resolver)
        self.object_cloth_description: ObjectDesignatorDescription = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def __iter__(self):
        for object_, arm in itertools.product(iter(self.object_cloth_description), self.arms):
            yield self.Action(object_, self.wipe_locations, self.lengths, self.widths, arm, 0.1)

    def ground(self) -> Action:
        return next(iter(self))
