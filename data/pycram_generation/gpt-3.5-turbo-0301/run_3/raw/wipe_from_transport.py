
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription, BelieveObject
from pycram.designators.location_designator import CostmapLocation
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.designators.action_designator import NavigateAction, ParkArmsAction, PickUpAction, PlaceAction
from pycram.robot_descriptions import robot_description
from pycram.enums import Arms
from pycram.pose import Pose
from typing import List, Union

class WipeAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]

        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            pickup_pose = None
            for pose in pickup_loc:
                if self.arms[0] in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth_designator} with arm: {self.arms[0]}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_designator, self.arms[0], "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            for i, loc in enumerate(self.wipe_locations):
                try:
                    place_loc = CostmapLocation(target=loc, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0]).resolve()
                except StopIteration:
                    raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {loc}")
                NavigateAction([place_loc.pose]).resolve().perform()
                PlaceAction.Action(self.object_cloth_designator, self.arms[0], loc).perform()
                MoveTCPMotion.Action(place_loc.pose, self.arms[0]).perform()
                length = self.lengths[i]
                width = self.widths[i]
                gap = 0.1
                num_strips = math.ceil(width / gap)
                for j in range(num_strips):
                    strip_center = Pose([loc.position[0], loc.position[1] - width / 2 + gap / 2 + j * gap, loc.position[2]], loc.orientation)
                    MoveTCPMotion.Action(strip_center, self.arms[0]).perform()
                    strip_start = Pose([strip_center.position[0] - length / 2, strip_center.position[1], strip_center.position[2]], strip_center.orientation)
                    strip_end = Pose([strip_center.position[0] + length / 2, strip_center.position[1], strip_center.position[2]], strip_center.orientation)
                    MoveTCPMotion.Action(strip_start, self.arms[0]).perform()
                    MoveTCPMotion.Action(strip_end, self.arms[0]).perform()
                PlaceAction.Action(self.object_cloth_designator, self.arms[0], loc).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms

    def ground(self) -> Action:
        obj_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
