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
        arms: List[str]

        def perform(self) -> None:
            cloth_object = self.object_cloth_designator.bullet_world_object
            cloth_pose = cloth_object.get_pose()
            cloth_dim = cloth_object.get_object_dimensions()

            for i, wipe_location in enumerate(self.wipe_locations):
                length = self.lengths[i]
                width = self.widths[i]
                arm = self.arms[i % len(self.arms)]

                # Calculate the number of strips
                num_strips = int(length / 0.1)

                # Calculate the starting position of the wipe
                start_pos = np.array([wipe_location.pose.position.x - length / 2, wipe_location.pose.position.y - width / 2, wipe_location.pose.position.z])

                # Calculate the direction of the wipe
                direction = np.array([1, 0, 0])

                # Calculate the distance between each strip
                strip_distance = length / num_strips

                # Calculate the gap between each strip
                gap = 0.1

                # Calculate the height of the cloth object
                cloth_height = cloth_dim[2]

                # Move the arm to the starting position
                start_pose = Pose(position=start_pos, frame="map")
                MoveTCPMotion(start_pose, arm).resolve().perform()

                # Wipe in a zigzag pattern
                for j in range(num_strips):
                    # Calculate the position of the current strip
                    strip_pos = start_pos + j * strip_distance * direction

                    # Calculate the position of the next strip
                    next_strip_pos = strip_pos + strip_distance * direction

                    # Calculate the position of the gap between the strips
                    gap_pos = strip_pos + (strip_distance - gap) * direction

                    # Move the arm to the current strip position
                    strip_pose = Pose(position=strip_pos, frame="map")
                    MoveTCPMotion(strip_pose, arm).resolve().perform()

                    # Move the arm down to the cloth object
                    cloth_pose.pose.position.z = cloth_height
                    MoveTCPMotion(cloth_pose, arm).resolve().perform()

                    # Move the arm up to the gap position
                    gap_pose = Pose(position=gap_pos, frame="map")
                    MoveTCPMotion(gap_pose, arm).resolve().perform()

                    # Move the arm down to the cloth object
                    cloth_pose.pose.position.z = cloth_height
                    MoveTCPMotion(cloth_pose, arm).resolve().perform()

                # Move the arm to the starting position
                MoveTCPMotion(start_pose, arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
