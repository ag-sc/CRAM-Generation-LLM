
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
            pickup_pose = next(pose for pose in pickup_loc if self.arms[0] in pose.reachable_arms)
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth_designator} with arm: {self.arms[0]}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_designator, self.arms[0], "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            for i in range(len(self.wipe_locations)):
                try:
                    wipe_loc = CostmapLocation(target=self.wipe_locations[i], reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0]).resolve()
                except StopIteration:
                    raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {self.wipe_locations[i]}")
                
                NavigateAction([wipe_loc.pose]).resolve().perform()
                MoveTCPMotion(self.wipe_locations[i], self.arms[0]).perform()
                for j in range(int(self.lengths[i] / 0.1)):
                    MoveTCPMotion(Pose([0.1 * j, 0, 0], [0, 0, 0, 1]), self.arms[0]).perform()
                    MoveTCPMotion(Pose([0.1 * j, self.widths[i], 0], [0, 0, 0, 1]), self.arms[0]).perform()
                ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        obj_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
