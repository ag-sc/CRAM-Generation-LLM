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
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the source object that should be poured
        """
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the container where the contents should be poured
        """
        arms: List[str]
        """
        The arms that should be used to pour
        """
        durations: List[float]
        """
        The duration of the pour in seconds
        """

        @with_tree
        def perform(self) -> None:
            # get pose of source object
            if isinstance(self.object_source_desig, ObjectPart.Object):
                source_pose = self.object_source_desig.part_pose
            else:
                source_pose = self.object_source_desig.bullet_world_object.get_pose()

            # get pose of container
            if isinstance(self.object_container_desig, ObjectPart.Object):
                container_pose = self.object_container_desig.part_pose
            else:
                container_pose = self.object_container_desig.bullet_world_object.get_pose()

            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arms[0])

            # calculate pour pose
            pour_pose = container_pose.copy()
            pour_pose.pose.position.z += 0.1
            pour_pose.pose.position.y += 0.1

            # move to source object and grasp it
            MoveTCPMotion(source_pose, self.arms[0]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()

            # move to container and pour contents
            MoveTCPMotion(pour_pose, self.arms[0], allow_gripper_collision=True).resolve().perform()
            MoveTCPMotion(pour_pose, self.arms[0], allow_gripper_collision=True, orientation=axis_angle_to_quaternion([1, 0, 0], math.pi/2)).resolve().perform()
            time.sleep(self.durations[0])
            MoveTCPMotion(pour_pose, self.arms[0], allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()


    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], durations: List[float], resolver=None):
        """
        Will try to pour the contents of the source object into the container. Pouring is done by moving to the source
        object, grasping it, moving to the container, tilting the source object at a 90° angle, and pouring its contents
        into the container for a specified duration.

        :param object_source_description: Description of the source object that should be poured
        :param object_container_description: Description of the container where the contents should be poured
        :param arms: List of Arms that should be used for pouring
        :param durations: List of durations of the pour in seconds
        :param resolver: An alternative resolver to get a specified designator from the designator description
        """
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        """
        Default resolver that takes the first element from the list of arms and durations and the first solution for the
        object designator descriptions and returns it.

        :return: A performable action designator that contains specific arguments
        """
        object_source_desig = self.object_source_description if (isinstance(self.object_source_description, ObjectDesignatorDescription.Object) or isinstance(self.object_source_description, ObjectPart.Object)) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if (isinstance(self.object_container_description, ObjectDesignatorDescription.Object) or isinstance(self.object_container_description, ObjectPart.Object)) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations[0])