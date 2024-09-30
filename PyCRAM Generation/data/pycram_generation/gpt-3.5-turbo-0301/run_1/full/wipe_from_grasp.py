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

















class WipeAction(ActionDesignatorDescription):
    """
    Wipes a rectangular part of a surface defined by the center, length, and width in a zigzag pattern with a 10 cm gap between the strips
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the cloth object that should be used for wiping
        """
        
        wipe_locations: List[Pose]
        """
        List of locations where the wiping should be done
        """

        lengths: List[float]
        """
        List of lengths of the rectangular part to be wiped at each location
        """

        widths: List[float]
        """
        List of widths of the rectangular part to be wiped at each location
        """

        arms: List[str]
        """
        List of Arms that should be used for wiping
        """

        @with_tree
        def perform(self) -> None:
            # get pose of cloth object
            if isinstance(self.object_cloth_desig, ObjectPart.Object):
                cloth_pose = self.object_cloth_desig.part_pose
            else:
                cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arms[0])

            cloth_pose_in_gripper = lt.transform_pose(cloth_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))

            # move to cloth object and pick it up
            PickUpAction(self.object_cloth_desig, self.arms, ["pinch"]).resolve().perform()

            # move to each wiping location and wipe in a zigzag pattern
            for i, loc in enumerate(self.wipe_locations):
                MoveTCPMotion(loc, self.arms[0]).resolve().perform()
                length = self.lengths[i]
                width = self.widths[i]
                gap = 0.1
                num_strips = math.ceil(width / gap)
                for j in range(num_strips):
                    if j % 2 == 0:
                        start = Pose([0, j * gap, 0], [0, 0, 0, 1])
                        end = Pose([length, j * gap, 0], [0, 0, 0, 1])
                    else:
                        start = Pose([length, (j + 1) * gap, 0], [0, 0, 0, 1])
                        end = Pose([0, (j + 1) * gap, 0], [0, 0, 0, 1])
                    MoveTCPMotion(lt.transform_pose(start, loc.frame), self.arms[0]).resolve().perform()
                    MoveTCPMotion(lt.transform_pose(end, loc.frame), self.arms[0]).resolve().perform()

            # place cloth object back
            PlaceAction(self.object_cloth_desig, self.wipe_locations, self.arms).resolve().perform()


    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        """
        Will try to wipe a rectangular part of a surface defined by the center, length, and width in a zigzag pattern with a 10 cm gap between the strips.

        :param object_cloth_description: Description of the cloth object that should be used for wiping
        :param wipe_locations: List of locations where the wiping should be done
        :param lengths: List of lengths of the rectangular part to be wiped at each location
        :param widths: List of widths of the rectangular part to be wiped at each location
        :param arms: List of Arms that should be used for wiping
        :param resolver: An alternative resolver to get a specified designator from the designator description
        """
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        """
        Default resolver that takes the first solution for the object cloth designator description and returns it.

        :return: A performable action designator that contains specific arguments
        """
        object_cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])