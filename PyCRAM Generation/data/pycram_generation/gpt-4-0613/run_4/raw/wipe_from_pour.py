
class WipeAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth} with arm: {self.arm}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            wipe_loc = CostmapLocation(target=self.wipe_location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                wipe_pose = next(iter(wipe_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to wipe the surface: {self.wipe_location} with arm: {self.arm}")

            NavigateAction([wipe_pose.pose]).resolve().perform()

            num_strips = math.ceil(self.length / 0.1)
            for i in range(num_strips):
                start_pose = Pose([wipe_pose.pose.position.x, wipe_pose.pose.position.y + i * 0.1, wipe_pose.pose.position.z], wipe_pose.pose.orientation)
                end_pose = Pose([wipe_pose.pose.position.x + self.width, wipe_pose.pose.position.y + i * 0.1, wipe_pose.pose.position.z], wipe_pose.pose.orientation)
                MoveTCPMotion(start_pose, self.arm).resolve().perform()
                MoveTCPMotion(end_pose, self.arm).resolve().perform()

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
        return self.Action(cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
