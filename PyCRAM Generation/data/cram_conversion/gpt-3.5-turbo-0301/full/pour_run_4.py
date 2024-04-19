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


















# Pose


# object designators


# location designators


# motion designators


# action designators


class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            world = BulletWorld()
            transformer = LocalTransformer(self.object_container.frame)
            source_desig = self.object_source.resolve()
            container_desig = self.object_container.resolve()
            source_pose = source_desig.pose
            container_pose = container_desig.pose
            source_type = source_desig.type
            container_type = container_desig.type
            source_name = source_desig.name
            container_name = container_desig.name
            source_size = source_desig.size
            container_size = container_desig.size
            source_mass = source_desig.mass
            container_mass = container_desig.mass
            source_grasps = source_desig.grasps
            container_grasps = container_desig.grasps
            source_transform = source_pose.transform
            container_transform = container_pose.transform
            source_to_container = container_transform.inverse() * source_transform
            source_to_container_position = source_to_container[:3, 3]
            source_to_container_orientation = source_to_container[:3, :3]
            source_to_container_quaternion = np.quaternion(*source_to_container_orientation)
            source_to_container_axis, source_to_container_angle = Pose.from_matrix(source_to_container).axis_angle
            source_to_container_axis_quaternion = axis_angle_to_quaternion(source_to_container_axis, source_to_container_angle)
            source_to_container_quaternion = multiply_quaternions(source_to_container_quaternion, source_to_container_axis_quaternion)
            source_to_container_pose = Pose(position=source_to_container_position, orientation=source_to_container_quaternion, frame=container_pose.frame)
            source_to_container_pose = transformer.transform(source_to_container_pose, self.object_container.frame)
            source_to_container_pose.position[2] += container_size[2] / 2 + source_size[2] / 2 + 0.2
            source_to_container_pose = transformer.transform(source_to_container_pose, "map")
            source_to_container_location = CostmapLocation(source_to_container_pose, reachable_for=self.object_source, visible_for=self.object_container, reachable_arm=self.arms[0]).resolve()
            source_to_container_motion = MoveTCPMotion(source_to_container_location.pose, arm=self.arms[0]).resolve()
            source_grasp = source_grasps[0]
            container_grasp = container_grasps[0]
            source_pickup = PickUpAction(self.object_source, self.arms, [source_grasp]).resolve()
            container_place = PlaceAction(self.object_container, [source_to_container_pose], self.arms).resolve()
            container_location = CostmapLocation(container_pose, reachable_for=self.object_container, visible_for=self.object_source, reachable_arm=self.arms[0]).resolve()
            container_motion = MoveTCPMotion(container_location.pose, arm=self.arms[0]).resolve()
            container_pickup = PickUpAction(self.object_container, self.arms, [container_grasp]).resolve()
            source_place = PlaceAction(self.object_source, [source_pose], self.arms).resolve()
            source_tilt_motion = MoveTCPMotion(source_to_container_pose, arm=self.arms[0]).resolve()
            gripper_open = MoveGripperMotion("open", self.arms[0]).resolve()
            gripper_close = MoveGripperMotion("close", self.arms[0]).resolve()
            gripper_effort = 0.5
            gripper_opening = 0.05
            duration = self.durations[0]
            trajectory = []
            for i in range(int(duration / 0.1)):
                tilt_angle = math.pi / 2 * min(1, (i + 1) * 0.1 / duration)
                tilt_quaternion = axis_angle_to_quaternion([0, 0, 1], tilt_angle)
                tilt_pose = Pose(position=source_to_container_pose.position, orientation=tilt_quaternion, frame=source_to_container_pose.frame)
                tilt_motion = MoveTCPMotion(tilt_pose, arm=self.arms[0]).resolve()
                trajectory += [source_to_container_motion, source_pickup, container_place, container_motion, container_pickup, source_place, source_tilt_motion, tilt_motion, gripper_open, MoveGripperMotion("effort", self.arms[0], gripper_effort), MoveGripperMotion("opening", self.arms[0], gripper_opening), gripper_close]
            for motion in trajectory:
                motion.perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms, self.durations)
