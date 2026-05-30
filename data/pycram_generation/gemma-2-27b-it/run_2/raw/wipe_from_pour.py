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
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            for i, wipe_location in enumerate(self.wipe_locations):
                for j in range(int(self.lengths[i] / 0.1)):
                    target_pose = Pose([wipe_location.position.x + j * 0.1, wipe_location.position.y, wipe_location.position.z], [1, 0, 0, 1])
                    MoveTCPMotion(target_pose, self.arm).resolve().perform()
                    time.sleep(0.5)
                    target_pose = Pose([wipe_location.position.x + j * 0.1, wipe_location.position.y + self.widths[i], wipe_location.position.z], [1, 0, 0, 1])
                    MoveTCPMotion(target_pose, self.arm).resolve().perform()
                    time.sleep(0.5)

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List