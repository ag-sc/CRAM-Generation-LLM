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
        wipe_location: Pose
        length: float
        width: float
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the cloth: {self.object_cloth_designator} with arm: {self.arm}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_designator, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            wipe_poses = self.generate_wipe_poses()
            for pose in wipe_poses:
                move_tcp_motion = MoveTCPMotion(target=pose, arm=self.arm)
                move_tcp_motion.resolve().perform()

            PlaceAction.Action(self.object_cloth_designator, self.arm, self.wipe_location).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

        def generate_wipe_poses(self) -> List[Pose]:
            wipe_poses = []
            num_strips = math.ceil(self.length / 0.1)
            for i in range(num_strips):
                x_offset = (i * 0.1) - (self.length / 2)
                for j in range(2):
                    y_offset = (-self.width / 2) if j == 0 else (self.width / 2)
                    position = [self.wipe_location.position[0] + x_offset, self.wipe_location.position[1] + y_offset, self.wipe_location.position[2]]
                    orientation = self.wipe_location.orientation
                    wipe_poses.append(Pose(position, orientation))
            return wipe_poses

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        obj_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
