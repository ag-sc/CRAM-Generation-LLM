
class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            for i in range(len(self.wipe_locations)):
                wipe_loc = CostmapLocation(target=self.wipe_locations[i], reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                try:
                    wipe_pose = next(iter(wipe_loc))
                except StopIteration:
                    raise ReachabilityFailure(f"Found no pose for the robot to wipe at location: {self.wipe_locations[i]} with arm: {self.arm}")

                NavigateAction([wipe_pose.pose]).resolve().perform()

                cloth_dimensions = self.object_cloth.bullet_world_object.get_object_dimensions()

                for j in range(int(self.lengths[i] / 0.1)):
                    for k in range(int(self.widths[i] / 0.1)):
                        wipe_pose = Pose([wipe_pose.pose.position.x + (-1) ** j * 0.1, wipe_pose.pose.position.y + (-1) ** k * 0.1, wipe_pose.pose.position.z], wipe_pose.pose.orientation)
                        MoveTCPMotion(wipe_pose, self.arm).resolve().perform()

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
