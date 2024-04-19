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
    """
    Pours the contents of an object into a container
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the source object that should be poured.
        """
        
        object_container_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the container where the contents should be poured.
        """
        
        arm: str
        """
        Arm that should be used
        """
        
        duration: float
        """
        Duration for which the object should be tilted to pour its contents
        """

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_source_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            # Tries to find a pick-up posotion for the robot that uses the given arm
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source_designator} with arm: {self.arm}")

            # navigate to pick-up position and pick up the object
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source_designator, self.arm, "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find position for robot to stand in when placing object
            try:
                place_loc = CostmapLocation(target=self.object_container_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            except StopIteration:
                raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {self.object_container_designator}")
            
            # navigate to target position and pour object
            NavigateAction([place_loc.pose]).resolve().perform()
            target_pose = Pose(position=[place_loc.pose.position.x, place_loc.pose.position.y, place_loc.pose.position.z + 0.2], orientation=axis_angle_to_quaternion([1, 0, 0, math.pi/2]))
            MoveTCPMotion(target_pose, self.arm).perform()
            time.sleep(self.duration)
            ParkArmsAction.Action(Arms.BOTH).perform()


    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        """
        Designator representing a pour plan.

        :param object_source_description: Object designator description or a specified Object designator that should be poured
        :param object_container_description: Object designator description or a specified Object designator for the container where the contents should be poured
        :param arms: A List of possible arms that could be used for transporting
        :param durations: A List of possible durations for tilting the object to pour its contents
        :param resolver: An alternative resolver that returns a performable designator for the list of possible parameter
        """
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        """
        Default resolver that returns a performable designator with the first entries from the lists of possible parameter.

        :return: A performable designator
        """
        obj_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        obj_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(obj_source_desig, obj_container_desig, self.arms[0], self.durations[0])
