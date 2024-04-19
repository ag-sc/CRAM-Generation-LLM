
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

# object designators
from pycram.designators.object_designator import BelieveObject, ObjectPart

# location designators
from pycram.designators.location_designator import CostmapLocation

# motion designators
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion

# action designators
from pycram.designators.action_designator import MoveTorsoAction, ParkArmsAction, PickUpAction, PlaceAction, NavigateAction

class WipeAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]

        @with_tree
        def perform(self) -> None:
            cloth = self.object_cloth.resolve()
            for i in range(len(self.wipe_locations)):
                location = self.wipe_locations[i]
                length = self.lengths[i]
                width = self.widths[i]
                arm = self.arms[i]
                gripper = "gripper_" + arm
                gripper_closed = "gripper_" + arm + "_closed"
                gripper_open = "gripper_" + arm + "_open"
                approach_pose = Pose(position=[location.position[0], location.position[1], location.position[2] + 0.1], orientation=location.orientation)
                move_approach = MoveTCPMotion(approach_pose, arm=arm)
                move_approach.resolve().perform()
                pick_up = PickUpAction(cloth, arms=[arm], grasps=[gripper_closed])
                pick_up.resolve().perform()
                move_up = MoveTCPMotion(Pose(position=[location.position[0], location.position[1], location.position[2] + 0.2], orientation=location.orientation), arm=arm)
                move_up.resolve().perform()
                move_wipe = MoveTCPMotion(Pose(position=[location.position[0] - length/2, location.position[1] - width/2, location.position[2] + 0.2], orientation=location.orientation), arm=arm)
                move_wipe.resolve().perform()
                for j in range(int(length/0.1)):
                    move_wipe = MoveTCPMotion(Pose(position=[location.position[0] - length/2 + j*0.1, location.position[1] - width/2 + (-1)**j*0.05, location.position[2] + 0.2], orientation=location.orientation), arm=arm)
                    move_wipe.resolve().perform()
                move_up.resolve().perform()
                place = PlaceAction(cloth, [location], arms=[arm])
                place.resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth, self.wipe_locations, self.lengths, self.widths, self.arms)
