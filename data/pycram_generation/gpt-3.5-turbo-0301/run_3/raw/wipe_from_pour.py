
from typing import List, Optional, Union
import dataclasses
import time
import math
import numpy as np

from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.pose import Pose
from pycram.designators.object_designator import BelieveObject, ObjectPart
from pycram.designators.location_designator import CostmapLocation
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
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
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the cloth object
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth} with arm: {self.arms[0]}")
            
            # navigate to cloth object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arms, "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # get the dimensions of the cloth object
            cloth_dimensions = self.object_cloth.bullet_world_object.get_object_dimensions()
            
            # loop through wipe locations and wipe in a zigzag pattern
            for i, loc in enumerate(self.wipe_locations):
                # determine the number of strips needed to cover the length and width of the wipe area
                num_strips_length = math.ceil(self.lengths[i] / 0.1)
                num_strips_width = math.ceil(self.widths[i] / 0.1)
                
                # determine the starting position for the wipe
                start_pos = Pose([loc.position[0] - 0.5*self.lengths[i], loc.position[1] - 0.5*self.widths[i], loc.position[2]], [1, 0, 0, 1])
                
                # loop through the strips and wipe in a zigzag pattern
                for j in range(num_strips_length):
                    # determine the position of the start of the strip
                    strip_start_pos = Pose([start_pos.position[0] + j*0.1, start_pos.position[1], start_pos.position[2]], [1, 0, 0, 1])
                    
                    # determine the direction of the strip
                    if j % 2 == 0:
                        strip_direction = [0, 1, 0]
                    else:
                        strip_direction = [0, -1, 0]
                    
                    # loop through the width of the strip and wipe in a zigzag pattern
                    for k in range(num_strips_width):
                        # determine the position of the start of the wipe
                        wipe_start_pos = Pose([strip_start_pos.position[0], strip_start_pos.position[1] + k*0.1, strip_start_pos.position[2]], [1, 0, 0, 1])
                        
                        # determine the direction of the wipe
                        if k % 2 == 0:
                            wipe_direction = [1, 0, 0]
                        else:
                            wipe_direction = [-1, 0, 0]
                        
                        # determine the end position of the wipe
                        wipe_end_pos = Pose([wipe_start_pos.position[0] + wipe_direction[0]*self.lengths[i], wipe_start_pos.position[1] + wipe_direction[1]*self.widths[i], wipe_start_pos.position[2] + cloth_dimensions[2]], [1, 0, 0, 1])
                        
                        # navigate to the start position of the wipe
                        NavigateAction([wipe_start_pos]).resolve().perform()
                        
                        # move the cloth to the end position of the wipe
                        MoveTCPMotion(wipe_end_pos, self.arms[0]).resolve().perform()
                        
                        # move the cloth back to the start position of the wipe
                        MoveTCPMotion(wipe_start_pos, self.arms[0]).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])