
from typing import List, Optional, Union
import dataclasses

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

class GraspAction(ActionDesignatorDescription):
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: ObjectDesignatorDescription.Object
        arms: List[str]
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to grasp the object
            grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                grasp_pose = next(iter(grasp_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arms[0]}")
            
            # navigate to pre-grasp position
            pre_grasp_pose = Pose([grasp_pose.pose.position.x - 0.1, grasp_pose.pose.position.y, grasp_pose.pose.position.z], [1, 0, 0, 1])
            NavigateAction([pre_grasp_pose]).resolve().perform()
            
            # open gripper
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            
            # navigate to grasp position and close gripper
            NavigateAction([grasp_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_description, self.arms[0], "front").perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
            
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
        
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms)
