
import dataclasses
from typing import List, Optional, Union
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.designators.action_designator import MoveTorsoAction, ParkArmsAction, PickUpAction, PlaceAction, NavigateAction
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.designators.location_designator import CostmapLocation
from pycram.designators.object_designator import BelieveObject, ObjectPart
from pycram.pose import Pose
from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer

class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            if self.technique == "halving":
                MoveTCPMotion(target=Pose(position=[0, 0, self.object_designator.height / 2], orientation=[0, 0, 0, 1], frame=self.object_designator.frame), arm=self.arm).resolve().perform()
                MoveTCPMotion(target=Pose(position=[0, 0, -self.object_designator.height / 2], orientation=[0, 0, 0, 1], frame=self.object_designator.frame), arm=self.arm).resolve().perform()
            elif self.technique == "slicing":
                slice_count = int(self.object_designator.width / self.slice_thickness)
                for i in range(slice_count):
                    MoveTCPMotion(target=Pose(position=[0, i * self.slice_thickness, self.object_designator.height / 2], orientation=[0, 0, 0, 1], frame=self.object_designator.frame), arm=self.arm).resolve().perform()
                    MoveTCPMotion(target=Pose(position=[0, i * self.slice_thickness, -self.object_designator.height / 2], orientation=[0, 0, 0, 1], frame=self.object_designator.frame), arm=self.arm).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
