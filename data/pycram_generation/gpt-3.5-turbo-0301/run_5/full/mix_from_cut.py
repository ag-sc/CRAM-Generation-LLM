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


class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            # Retrieve object and robot from designators
            object_bowl = self.object_bowl_designator.bullet_world_object
            oTm = object_bowl.get_pose()
            object_bowl_pose = object_bowl.local_transformer.transform_to_object_frame(oTm, object_bowl)

            # Get grasp orientation and target pose
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)

            # Define mixing parameters
            radius = 0.05
            height = 0.02
            num_circles = 3
            num_points_per_circle = 20
            angle_step = 2 * math.pi / num_points_per_circle
            z_step = height / num_points_per_circle

            # Calculate mixing trajectory
            mixing_trajectory = []
            for i in range(num_circles):
                for j in range(num_points_per_circle):
                    angle = i * angle_step + j * angle_step
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    z = i * z_step
                    mixing_trajectory.append([x, y, z])

            # Transform mixing trajectory to map frame with orientation
            mixing_poses = []
            for point in mixing_trajectory:
                tmp_pose = object_bowl_pose.copy()
                tmp_pose.pose.position.x += point[0]
                tmp_pose.pose.position.y += point[1]
                tmp_pose.pose.position.z += point[2]
                sTm = object_bowl.local_transformer.transform_pose(tmp_pose, "map")
                mixing_poses.append(sTm)

            # Perform mixing motion
            for pose in mixing_poses:
                # rotate the pose by grasp
                ori = multiply_quaternions([pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w], grasp)

                adjusted_pose = pose.copy()

                # Set the orientation of the object pose by grasp in MAP
                adjusted_pose.orientation.x = ori[0]
                adjusted_pose.orientation.y = ori[1]
                adjusted_pose.orientation.z = ori[2]
                adjusted_pose.orientation.w = ori[3]

                # Perform the motion for mixing the object
                MoveTCPMotion(adjusted_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
