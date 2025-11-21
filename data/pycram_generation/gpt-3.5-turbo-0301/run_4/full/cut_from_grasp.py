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
    """
    Cuts an object described by the given Object Designator description
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the object that should be cut
        """
        
        arm: str
        """
        The arm that should be used to cut
        """

        grasp: str
        """
        The grasp that should be used to hold the tool
        """

        technique: str
        """
        The technique that should be used to cut the object (halving or slicing)
        """

        slice_thickness: float
        """
        The thickness of each slice (only used for slicing technique)
        """

        @with_tree
        def perform(self) -> None:
            # get pose of object to be cut
            if isinstance(self.object_desig, ObjectPart.Object):
                object_pose = self.object_desig.part_pose
            else:
                object_pose = self.object_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            tool_name = robot_description.get_tool_frame(self.arm)

            # calculate cut poses
            if self.technique == "halving":
                cut_poses = [object_pose.copy()]
                cut_poses[0].pose.position.z += 0.05
                cut_poses.append(object_pose.copy())
                cut_poses[1].pose.position.z -= 0.05
            elif self.technique == "slicing":
                object_width = self.object_desig.bullet_world_object.get_dimensions()[0]
                num_slices = int(object_width / self.slice_thickness)
                cut_poses = [object_pose.copy()]
                for i in range(1, num_slices):
                    new_pose = object_pose.copy()
                    new_pose.pose.position.y += i * self.slice_thickness
                    cut_poses.append(new_pose)

            # move to cut poses and perform cut
            for pose in cut_poses:
                pose_in_tool = lt.transform_pose(pose, BulletWorld.robot.get_link_tf_frame(tool_name))
                MoveTCPMotion(pose_in_tool, self.arm).resolve().perform()
                MoveGripperMotion(self.grasp, self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        """
        Will try to cut the object described by the given description. Cutting is done by performing a vertical slicing
        motion along the middle of the object (halving) or along the width of the object (slicing) using a tool in a
        specified arm with a specified grasp.

        :param object_description: Description of the object that should be cut
        :param arms: List of Arms that should be used for cutting
        :param grasps: List of Grasps that should be used to hold the tool
        :param techniques: List of Techniques that should be used to cut the object (halving or slicing)
        :param slice_thicknesses: List of slice thicknesses to use for slicing (default is 0.05)
        :param resolver: An alternative resolver to get a specified designator from the designator description
        """
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        """
        Default resolver that takes the first element from the list of arms, grasps, techniques, and slice thicknesses
        and the first solution for the object designator description and returns it.

        :return: A performable action designator that contains specific arguments
        """
        object_desig = self.object_description if (isinstance(self.object_description, ObjectDesignatorDescription.Object) or isinstance(self.object_description, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])