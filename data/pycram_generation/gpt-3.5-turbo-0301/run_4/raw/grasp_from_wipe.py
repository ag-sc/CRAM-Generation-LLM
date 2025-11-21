
from typing import List, Union
from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.designators.action_designator import NavigateAction, ParkArmsAction

class GraspAction(ActionDesignatorDescription):
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object]
        arms: List[str]
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location for pre-grasp position
            pre_grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pre_grasp_pose = next(iter(pre_grasp_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arms[0]}")
            
            # navigate to pre-grasp position and open gripper
            NavigateAction([pre_grasp_pose.pose]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            
            # find location for grasp position
            grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                grasp_pose = next(iter(grasp_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arms[0]}")
            
            # navigate to grasp position and close gripper
            NavigateAction([grasp_pose.pose]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms)
