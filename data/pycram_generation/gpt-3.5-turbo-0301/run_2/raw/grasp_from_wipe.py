
from typing import List, Union
import dataclasses
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.designators.action_designator import NavigateAction, PickUpAction
from pycram.robot_descriptions import robot_description
from pycram.enums import Arms
from pycram.pose import Pose

@dataclasses.dataclass
class GraspAction(ActionDesignatorDescription.Action):
    object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object]
    arms: List[str]
    
    def perform(self) -> None:
        robot_desig = ObjectDesignatorDescription.BelieveObject(names=[robot_description.name])
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        reachable_for = robot_desig.resolve()
        reachable_arm = self.arms[0]
        pre_grasp_distance = 0.1
        
        # find location for pre-grasp position
        pre_grasp_loc = NavigateAction([Pose(position=[object_desig.pose.position.x - pre_grasp_distance, object_desig.pose.position.y, object_desig.pose.position.z])], resolver=None, reachable_for=reachable_for).resolve()
        pre_grasp_pose = next(iter(pre_grasp_loc))
        
        # move to pre-grasp position and open gripper
        MoveTCPMotion(pre_grasp_pose.pose, arm=reachable_arm, resolver=None, allow_gripper_collision=None).resolve().perform()
        MoveGripperMotion("open", reachable_arm, resolver=None, allow_gripper_collision=None).resolve().perform()
        
        # move to object and pick it up
        PickUpAction(object_desig, self.arms, "top", resolver=None, reachable_for=reachable_for, reachable_arm=reachable_arm).resolve().perform()
        
    def __repr__(self):
        return f"GraspAction({self.object_description}, {self.arms})"
    
class GraspActionDesignator(ActionDesignatorDescription):
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
        
    def ground(self) -> GraspAction:
        return GraspAction(self.object_description, self.arms)
