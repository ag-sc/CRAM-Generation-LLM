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
        object_to_cut: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the cutting tool
            pickup_loc = CostmapLocation(target=self.object_to_cut, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_to_cut} with arm: {self.arm}")
            
            # navigate to cutting tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_to_cut, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location for performing cut
            cut_loc = CostmapLocation(target=self.object_to_cut, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                cut_pose = next(iter(cut_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
            
            # navigate to cutting location
            NavigateAction([cut_pose.pose]).resolve().perform()
            
            # determine coordinates of middle of the object to be cut
            object_pose = self.object_to_cut.get_pose().resolve()
            object_length = object_pose.bounding_box.dimensions.x
            object_width = object_pose.bounding_box.dimensions.y
            object_height = object_pose.bounding_box.dimensions.z
            location_x = object_pose.position.x
            location_y = object_pose.position.y
            location_z = object_pose.position.z + 0.5*object_height
            
            if self.technique == "halving":
                # move cutting tool to top of object
                new_pose = Pose([location_x, location_y, location_z])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        cut_pose = next(iter(cut_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                    NavigateAction([cut_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
                
                # move cutting tool down to bottom of object
                new_pose = Pose([location_x, location_y, location_z-object_height])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        cut_pose = next(iter(cut_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                    NavigateAction([cut_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
            
            elif self.technique == "slicing":
                # determine number of slices to make
                num_slices = int(object_width/self.slice_thickness)
                
                # iterate over slices to be made
                for i in range(num_slices):
                    # move cutting tool to left side of slice
                    new_pose = Pose([location_x-0.5*object_length, location_y+i*self.slice_thickness, location_z])
                    try:
                        MoveTCPMotion(new_pose).resolve().perform()
                    except IKError:
                        cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                        try:
                            cut_pose = next(iter(cut_loc))
                        except StopIteration:
                            raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                        NavigateAction([cut_pose.pose]).resolve().perform()
                        MoveTCPMotion(new_pose).resolve().perform()
                    
                    # move cutting tool to right side of slice
                    new_pose = Pose([location_x+0.5*object_length, location_y+i*self.slice_thickness, location_z])
                    try:
                        MoveTCPMotion(new_pose).resolve().perform()
                    except IKError:
                        cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                        try:
                            cut_pose = next(iter(cut_loc))
                        except StopIteration:
                            raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                        NavigateAction([cut_pose.pose]).resolve().perform()
                        MoveTCPMotion(new_pose).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
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
