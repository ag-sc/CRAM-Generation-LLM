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
    Cuts an object in half or slices an object with a specified slice thickness.
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: ObjectDesignatorDescription.Object
        """
        Object designator describing the object that should be cut or sliced.
        """
        arm: str
        """
        Arm that should be used.
        """
        grasp: str
        """
        Grasp that should be used.
        """
        technique: str
        """
        Technique that should be used for cutting or slicing.
        """
        slice_thickness: float
        """
        Thickness of each slice. Only used for slicing technique.
        """
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the object
            pickup_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arm}")
            
            # navigate to object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_description, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # get the dimensions of the object
            object_dimensions = self.object_description.bullet_world_object.get_object_dimensions()
            
            # get the position of the object
            object_position = self.object_description.pose.position
            
            # determine the gripper pose for cutting/slicing
            if self.technique == "halving":
                cut_pose = Pose([object_position.x, object_position.y, object_position.z+0.5*object_dimensions[2]], [1, 0, 0, 1])
            elif self.technique == "slicing":
                cut_pose = Pose([object_position.x, object_position.y, object_position.z+0.5*object_dimensions[2]], [1, 0, 0, 1])
            
            # find location for cutting/slicing
            cut_loc = CostmapLocation(target=cut_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                cut_pose = next(iter(cut_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to cut/slice the object: {self.object_description} with arm: {self.arm}")
                
            # navigate to cutting/slicing location
            NavigateAction([cut_pose.pose]).resolve().perform()
            
            # perform cutting/slicing
            if self.technique == "halving":
                MoveTCPMotion(Pose([object_position.x, object_position.y, object_position.z+0.5*object_dimensions[2]-0.01], [1, 0, 0, 1]), self.arm).resolve().perform()
            elif self.technique == "slicing":
                for i in range(int(object_dimensions[1]/self.slice_thickness)):
                    MoveTCPMotion(Pose([object_position.x, object_position.y+0.5*object_dimensions[1]-i*self.slice_thickness, object_position.z+0.5*object_dimensions[2]-0.01], [1, 0, 0, 1]), self.arm).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        """
        Designator describing the action of cutting or slicing an object.
        
        :param object_designator_description: Object designator description or Object designator that should be cut or sliced
        :param arms: List of arms to be used for action
        :param grasps: List of grasps to be used for action
        :param techniques: List of techniques to be used for cutting or slicing
        :param slice_thicknesses: List of slice thicknesses to be used for slicing. Default is [0.05].
        :param resolver: Alternative resolver returning a performable designator
        """
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        """
        Default resolver uses first entries of provided parameter lists
        
        :return: Performable designator
        """
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
