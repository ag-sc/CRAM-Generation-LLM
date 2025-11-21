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










@dataclasses.dataclass
class MixAction(ActionDesignatorDescription.Action):
    object_bowl_description: ObjectDesignatorDescription.Object
    arms: List[str]
    grasps: List[str]

    @staticmethod
    def spiral_motion(center: Pose, radius: float, height: float, angle: float, steps: int) -> List[Pose]:
        poses = []
        for i in range(steps):
            x = center.position[0] + radius * math.cos(angle * i)
            y = center.position[1] + radius * math.sin(angle * i)
            z = center.position[2] + height * i / steps
            orientation = center.orientation
            poses.append(Pose(position=[x, y, z], orientation=orientation))
        return poses

    @with_tree
    def perform(self) -> None:
        robot_desig = BelieveObject(names=[robot_description.name])
        ParkArmsAction.Action(Arms.BOTH).perform()
        bowl_loc = NavigateAction([self.object_bowl_description]).resolve()
        NavigateAction([bowl_loc.pose]).resolve().perform()
        MoveTCPMotion(target=Pose(position=[0.0, 0.0, 0.1], frame="gripper_tool_frame"), arm=self.arms[0]).resolve().perform()
        poses = self.spiral_motion(bowl_loc.pose, 0.05, 0.02, 2 * math.pi, 20)
        for pose in poses:
            NavigateAction([pose]).resolve().perform()
        MoveTCPMotion(target=Pose(position=[0.0, 0.0, 0.1], frame="gripper_tool_frame"), arm=self.arms[0]).resolve().perform()
        ParkArmsAction.Action(Arms.BOTH).perform()

class MixAction(ActionDesignatorDescription):
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps

    def ground(self) -> MixAction:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return MixAction(obj_desig, self.arms, self.grasps)
