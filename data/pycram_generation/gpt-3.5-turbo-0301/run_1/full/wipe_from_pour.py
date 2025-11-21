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
                # determine the start and end points of the wipe
                start_x = loc.position[0] - 0.5*self.lengths[i]
                end_x = loc.position[0] + 0.5*self.lengths[i]
                start_y = loc.position[1] - 0.5*self.widths[i]
                end_y = loc.position[1] + 0.5*self.widths[i]
                
                # determine the number of strips needed to cover the width of the wipe
                num_strips = math.ceil(self.widths[i]/0.1)
                
                # determine the direction of the first strip
                direction = 1 if i%2 == 0 else -1
                
                # loop through the strips and wipe in a zigzag pattern
                for j in range(num_strips):
                    # determine the start and end points of the strip
                    strip_start_y = start_y + j*0.1*direction
                    strip_end_y = strip_start_y + 0.1*direction
                    
                    # determine the pose for wiping the strip
                    wipe_pose = Pose([start_x, (strip_start_y+strip_end_y)/2, loc.position[2]+0.1], [1, 0, 0, 1])
                    
                    # find location for wiping the strip
                    wipe_loc = CostmapLocation(target=wipe_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
                    try:
                        wipe_pose = next(iter(wipe_loc))
                    except StopIteration:
                        raise ReachabilityFailure(f"Found no pose for the robot to wipe at location: {wipe_pose} with arm: {self.arms[0]}")
                        
                    # navigate to wiping location and wipe
                    NavigateAction([wipe_pose.pose]).resolve().perform()
                    MoveTCPMotion(wipe_pose, self.arms[0]).resolve().perform()
                    time.sleep(0.5)
                    
                # reverse direction for next wipe
                direction *= -1
                
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
        return self.Action(cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
