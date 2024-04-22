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
    Designator to let the robot perform a cutting action.
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the object that should be cut.
        """

        arm: str
        """
        The arm that should be used for cutting.
        """

        grasp: str
        """
        The grasp that should be used for cutting. For example, 'left' or 'right'.
        """

        technique: str
        """
        The technique that should be used for cutting. For example, 'halving' or 'slicing'.
        """

        slice_thickness: float
        """
        The thickness of the slices to be cut. Only used if technique is 'slicing'.
        """

        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        """
        The object at the time this Action got created. It is used to be a static, information holding entity. It is
        not updated when the BulletWorld object is changed.
        """

        @with_tree
        def perform(self) -> None:
            """
            Perform the cutting action using the specified object, tool, arm, grasp, technique, and slice thickness.
            """
            # Store the object's data copy at execution
            self.object_at_execution = self.object_designator.data_copy()
            # Retrieve object and robot from designators
            object = self.object_designator.bullet_world_object

            obj_dim = object.get_object_dimensions()

            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            obj_width = dim[0]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            # method for generating vertical slicing trajectory
            def generate_vertical_slicing(pose, slice_thickness, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                slicing_poses = []

                for t in range(steps):
                    tmp_pose = pose.copy()

                    z = z_start + slice_thickness * t

                    tmp_pose.pose.position.z += z

                    slicingTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    slicing_poses.append(slicingTm)
                    BulletWorld.current_bullet_world.add_vis_axis(slicingTm)

                return slicing_poses

            # calculate trajectory
            if self.technique == 'halving':
                slice_thickness = obj_height / 2
                slicing_poses = generate_vertical_slicing(object_pose, slice_thickness, 2)
            elif self.technique == 'slicing':
                slicing_poses = generate_vertical_slicing(object_pose, self.slice_thickness, int(obj_width / self.slice_thickness))

            BulletWorld.current_bullet_world.remove_vis_axis()

            # perform cutting
            for slicing_pose in slicing_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([slicing_pose.orientation.x, slicing_pose.orientation.y, slicing_pose.orientation.z, slicing_pose.orientation.w], oriR)
                adjusted_cut_pose = slicing_pose.copy()
                # Set the orientation of the object pose by grasp in MAP
                adjusted_cut_pose.orientation.x = ori[0]
                adjusted_cut_pose.orientation.y = ori[1]
                adjusted_cut_pose.orientation.z = ori[2]
                adjusted_cut_pose.orientation.w = ori[3]

                # Adjust the position of the object pose by grasp in MAP
                lift_pose = adjusted_cut_pose.copy()
                lift_pose.pose.position.z += (obj_height + 0.08)
                # Perform the motion for lifting the tool
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()


    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        """
        Initialize the CutAction with object designator, arms, grasps, techniques, and slice thicknesses.

        :param object_designator_description: Object designator description or Object designator for the object to be cut.
        :param arms: List of possible arms that could be used.
        :param grasps: List of possible grasps for the cutting action.
        :param techniques: List of possible techniques for the cutting action. For example, 'halving' or 'slicing'.
        :param slice_thicknesses: List of possible slice thicknesses for the slicing technique. Only used if technique is 'slicing'.
        :param resolver: An optional resolver for dynamic parameter selection.
        """
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        """
        Default resolver, returns a performable designator with the first entries from the lists of possible parameter.

        :return: A performable designator
        """
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
