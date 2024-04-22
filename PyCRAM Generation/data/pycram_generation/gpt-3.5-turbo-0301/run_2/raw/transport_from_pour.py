
from typing import List, Optional, Union
import dataclasses
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription, BelieveObject
from pycram.designators.location_designator import CostmapLocation
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.designators.action_designator import NavigateAction, PickUpAction, PlaceAction, ParkArmsAction
from pycram.robot_descriptions import robot_description
from pycram.enums import Arms
from pycram.pose import Pose

class TransportAction(ActionDesignatorDescription):
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: ObjectDesignatorDescription.Object
        arm: str
        target_locations: List[Pose]
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the object
            pickup_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arm}")
            
            # navigate to object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_description, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # navigate to target location and place object down
            for target_location in self.target_locations:
                target_loc = CostmapLocation(target=target_location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                try:
                    target_pose = next(iter(target_loc))
                except StopIteration:
                    raise ReachabilityFailure(f"Found no pose for the robot to reach the target location: {target_location}")
                
                NavigateAction([target_pose.pose]).resolve().perform()
                PlaceAction.Action(self.object_description, [target_pose.pose], self.arm).perform()
                ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations)
