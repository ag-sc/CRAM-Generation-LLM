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
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            source_desig = self.object_source.resolve()
            container_desig = self.object_container.resolve()
            target_pose = Pose(position=[container_desig.pose.position[0], container_desig.pose.position[1], container_desig.pose.position[2] + 0.2], orientation=[0, 0, math.sin(math.pi/4), math.cos(math.pi/4)], frame=container_desig.pose.frame)
            approach_poses = []
            tilt_poses = []
            for arm in self.arms:
                if arm == Arms.LEFT:
                    approach_poses.append(Pose(position=[target_pose.position[0] - 0.1, target_pose.position[1], target_pose.position[2]], orientation=target_pose.orientation, frame=target_pose.frame))
                    tilt_poses.append(Pose(position=[target_pose.position[0], target_pose.position[1], target_pose.position[2]], orientation=[0, 0, math.sin(math.pi/2), math.cos(math.pi/2)], frame=target_pose.frame))
                elif arm == Arms.RIGHT:
                    approach_poses.append(Pose(position=[target_pose.position[0] + 0.1, target_pose.position[1], target_pose.position[2]], orientation=target_pose.orientation, frame=target_pose.frame))
                    tilt_poses.append(Pose(position=[target_pose.position[0], target_pose.position[1], target_pose.position[2]], orientation=[0, 0, math.sin(-math.pi/2), math.cos(-math.pi/2)], frame=target_pose.frame))
            move_source = MoveTCPMotion(target=source_desig.pose, arm=self.arms[0])
            move_container = MoveTCPMotion(target=target_pose, arm=self.arms[0])
            tilt_source = MoveTCPMotion(target=tilt_poses[0], arm=self.arms[0])
            tilt_container = MoveTCPMotion(target=tilt_poses[0], arm=self.arms[0])
            pour_duration = self.durations[0]
            # perform the actions
            move_source.resolve().perform()
            move_container.resolve().perform()
            time.sleep(1)  # wait for the robot to stabilize
            tilt_source.resolve().perform()
            tilt_container.resolve().perform()
            time.sleep(pour_duration)
            tilt_source.resolve().perform()  # return to original position
            tilt_container.resolve().perform()  # return to original position

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations)
