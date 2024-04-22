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






















class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object
            obj_dim = object.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            def generate_spiral(pose, upward_increment, radial_increment, angle_increment, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                spiral_poses = []

                for t in range(2 * steps):
                    tmp_pose = pose.copy()

                    r = radial_increment * t
                    a = angle_increment * t
                    h = upward_increment * t

                    x = x_start + r * math.cos(a)
                    y = y_start + r * math.sin(a)
                    z = z_start + h

                    tmp_pose.pose.position.x += x
                    tmp_pose.pose.position.y += y
                    tmp_pose.pose.position.z += z

                    spiralTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    spiral_poses.append(spiralTm)
                    BulletWorld.current_bullet_world.add_vis_axis(spiralTm)

                return spiral_poses

            if self.technique == "halving":
                # calculate trajectory
                spiral_poses = generate_spiral(object_pose, 0.001, 0.0035, math.radians(30), 10)
                BulletWorld.current_bullet_world.remove_vis_axis()

                # perform cutting
                for spiral_pose in spiral_poses:
                    oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                    ori = multiply_quaternions([spiral_pose.orientation.x, spiral_pose.orientation.y, spiral_pose.orientation.z, spiral_pose.orientation.w], oriR)
                    adjusted_cut_pose = spiral_pose.copy()
                    adjusted_cut_pose.orientation.x = ori[0]
                    adjusted_cut_pose.orientation.y = ori[1]
                    adjusted_cut_pose.orientation.z = ori[2]
                    adjusted_cut_pose.orientation.w = ori[3]

                    # Adjust the position of the object pose by grasp in MAP
                    lift_pose = adjusted_cut_pose.copy()
                    lift_pose.pose.position.z += (obj_height / 2)
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()

            elif self.technique == "slicing":
                # calculate trajectory
                spiral_poses = generate_spiral(object_pose, 0.001, 0.0035, math.radians(30), 10)
                BulletWorld.current_bullet_world.remove_vis_axis()

                # perform cutting
                for spiral_pose in spiral_poses:
                    oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                    ori = multiply_quaternions([spiral_pose.orientation.x, spiral_pose.orientation.y, spiral_pose.orientation.z, spiral_pose.orientation.w], oriR)
                    adjusted_cut_pose = spiral_pose.copy()
                    adjusted_cut_pose.orientation.x = ori[0]
                    adjusted_cut_pose.orientation.y = ori[1]
                    adjusted_cut_pose.orientation.z = ori[2]
                    adjusted_cut_pose.orientation.w = ori[3]

                    # Adjust the position of the object pose by grasp in MAP
                    lift_pose = adjusted_cut_pose.copy()
                    lift_pose.pose.position.z += (obj_height / 2)
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()

                    # Perform the motion for slicing the object
                    slice_poses = generate_spiral(lift_pose, self.slice_thickness, 0, 0, 1)
                    for slice_pose in slice_poses:
                        MoveTCPMotion(slice_pose, self.arm).resolve().perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
