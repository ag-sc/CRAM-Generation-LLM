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
            source_grasp = self.grasp
            container_grasp = self.grasp
            source_arm = self.arms[0]
            container_arm = self.arms[1]
            source_duration = self.durations[0]
            container_duration = self.durations[1]
            source_approach_poses = []
            container_approach_poses = []
            source_tilt_poses = []
            container_tilt_poses = []
            source_collision_mode = None
            container_collision_mode = None

            # get object transform
            source_transform = transformer.transform_pose(source_pose, "base_link")
            container_transform = transformer.transform_pose(container_pose, "base_link")

            # calculate object faces
            facing_robot_face, bottom_face = calculate_object_faces(source_transform)

            # infer missing information
            rotationally_symmetric = object_rotationally_symmetric(source_type)
            if rotationally_symmetric:
                source_grasp = "top"
            else:
                source_grasp = "side"
            source_gripping_effort = get_action_gripping_effort(source_type)
            source_gripper_opening = get_action_gripper_opening(source_type)
            container_gripping_effort = get_action_gripping_effort(container_type)
            container_gripper_opening = get_action_gripper_opening(container_type)

            # calculate trajectory
            objects = [source_desig, container_desig]
            if source_arm == "left":
                source_pouring_pose = get_action_trajectory("pouring", "left", source_grasp, True, objects)
                source_approach_poses = get_traj_poses_by_label(source_pouring_pose, "approach")
                source_tilt_poses = get_traj_poses_by_label(source_pouring_pose, "tilting")
            elif source_arm == "right":
                source_pouring_pose = get_action_trajectory("pouring", "right", source_grasp, True, objects)
                source_approach_poses = get_traj_poses_by_label(source_pouring_pose, "approach")
                source_tilt_poses = get_traj_poses_by_label(source_pouring_pose, "tilting")
            if container_arm == "left":
                container_pouring_pose = get_action_trajectory("pouring", "left", container_grasp, True, objects)
                container_approach_poses = get_traj_poses_by_label(container_pouring_pose, "approach")
                container_tilt_poses = get_traj_poses_by_label(container_pouring_pose, "tilting")
            elif container_arm == "right":
                container_pouring_pose = get_action_trajectory("pouring", "right", container_grasp, True, objects)
                container_approach_poses = get_traj_poses_by_label(container_pouring_pose, "approach")
                container_tilt_poses = get_traj_poses_by_label(container_pouring_pose, "tilting")

            # perform action
            source_approach_motion = MoveTCPMotion(source_approach_poses[0], source_arm)
            source_tilt_motion = MoveTCPMotion(source_tilt_poses[0], source_arm)
            container_approach_motion = MoveTCPMotion(container_approach_poses[0], container_arm)
            container_tilt_motion = MoveTCPMotion(container_tilt_poses[0], container_arm)
            source_gripper_motion = MoveGripperMotion("open", source_arm)
            container_gripper_motion = MoveGripperMotion("open", container_arm)
            source_duration_motion = MoveTCPMotion(source_tilt_poses[0], source_arm, duration=source_duration)
            container_duration_motion = MoveTCPMotion(container_tilt_poses[0], container_arm, duration=container_duration)
            source_gripper_close_motion = MoveGripperMotion("close", source_arm)
            container_gripper_close_motion = MoveGripperMotion("close", container_arm)
            source_gripper_open_motion = MoveGripperMotion("open", source_arm)
            container_gripper_open_motion = MoveGripperMotion("open", container_arm)

            try:
                source_approach_motion.perform()
                source_gripper_motion.perform()
                source_tilt_motion.perform()
                source_duration_motion.perform()
                source_gripper_close_motion.perform()
                container_approach_motion.perform()
                container_gripper_motion.perform()
                container_tilt_motion.perform()
                container_duration_motion.perform()
                container_gripper_close_motion.perform()
                source_gripper_open_motion.perform()
                container_gripper_open_motion.perform()
            except:
                raise IKError("IK Error")

            # put together resulting action designator
            return self.Action(source_desig, container_desig, self.arms, self.durations)

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
