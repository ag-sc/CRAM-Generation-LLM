
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

class MixAction(ActionDesignatorDescription):
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the tool
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the tool: {self.object_bowl} with arm: {self.arm}")
            
            # navigate to tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # get the dimensions of the bowl
            bowl_dimensions = self.object_bowl.bullet_world_object.get_object_dimensions()
            
            # get the position of the bowl
            bowl_position = self.object_bowl.pose.position
            
            # determine the gripper pose for mixing, top of tool should be 0.2 m above center of bowl
            tool_pose = Pose([bowl_position.x, bowl_position.y, bowl_position.z+0.2+bowl_dimensions[2]/2], [1, 0, 0, 1])
            
            # mix in bowl using a counterclockwise, outward spiraling motion
            for i in range(10):
                MoveTCPMotion(Pose([tool_pose.position[0]+0.05*i, tool_pose.position[1]+0.05*i, tool_pose.position[2]], tool_pose.orientation), self.arm).resolve().perform()
                time.sleep(0.5)
            
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
