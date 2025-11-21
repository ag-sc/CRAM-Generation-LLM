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
    Cuts an object in half (halving) by performing a vertical slicing motion along the middle of a specified object
    or cuts an object in slices (slicing) with a specified slice thickness by performing vertical slicing motions along
    the width of a specified object using a tool in a specified arm using a specified grasp.
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the object that should be cut.
        """
        
        arm: str
        """
        Arm that should be used for cutting
        """
        
        grasp: str
        """
        Grasp that should be used for cutting
        """
        
        technique: str
        """
        Technique that should be used for cutting (halving or slicing)
        """
        
        slice_thickness: float
        """
        Thickness of each slice (only used for slicing technique)
        """

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            # Tries to find a pick-up posotion for the robot that uses the given arm
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_designator} with arm: {self.arm}")

            # navigate to pick-up position and pick up the object
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find position for robot to stand in when cutting object
            try:
                cut_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            except StopIteration:
                raise ReachabilityFailure(f"No location found from where the robot can reach the object: {self.object_designator}")
            
            # navigate to cutting position and cut object
            NavigateAction([cut_loc.pose]).resolve().perform()
            if self.technique == "halving":
                MoveTCPMotion.Action(Pose(position=[0, 0, 0.1]), self.arm).perform()
                MoveTCPMotion.Action(Pose(position=[0, 0, -0.1]), self.arm).perform()
            elif self.technique == "slicing":
                for i in range(int(self.object_designator.bounding_box.dimensions[1] / self.slice_thickness)):
                    MoveTCPMotion.Action(Pose(position=[0, self.slice_thickness, 0]), self.arm).perform()
                    PlaceAction.Action(self.object_designator, self.arm, self.object_designator.pose).perform()
                    MoveTCPMotion.Action(Pose(position=[0, -self.slice_thickness, 0]), self.arm).perform()
                    PlaceAction.Action(self.object_designator, self.arm, self.object_designator.pose).perform()
            else:
                raise ValueError(f"Invalid cutting technique: {self.technique}")
            
            ParkArmsAction.Action(Arms.BOTH).perform()


    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        """
        Designator representing a cutting plan.

        :param object_designator_description: Object designator description or a specified Object designator that should be cut
        :param arms: A List of possible arms that could be used for cutting
        :param grasps: A List of possible grasps that could be used for cutting
        :param techniques: A List of possible cutting techniques (halving or slicing)
        :param slice_thicknesses: A List of possible slice thicknesses (only used for slicing technique)
        :param resolver: An alternative resolver that returns a performable designator for the list of possible parameter
        """
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        """
        Default resolver that returns a performable designator with the first entries from the lists of possible parameter.

        :return: A performable designator
        """
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
