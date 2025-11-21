
class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the cloth: {self.object_cloth_designator} with arm: {self.arm}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_designator, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            num_strips = math.ceil(self.length / 0.1)
            for i in range(num_strips):
                offset = i * 0.1
                start_x = self.wipe_location.position[0] - self.length / 2 + offset
                start_y = self.wipe_location.position[1] - self.width / 2
                end_x = start_x
                end_y = self.wipe_location.position[1] + self.width / 2
                start_pose = Pose([start_x, start_y, self.wipe_location.position[2]], self.wipe_location.orientation, self.wipe_location.frame)
                end_pose = Pose([end_x, end_y, self.wipe_location.position[2]], self.wipe_location.orientation, self.wipe_location.frame)
                move_start = MoveTCPMotion(target=start_pose, arm=self.arm)
                move_end = MoveTCPMotion(target=end_pose, arm=self.arm)
                move_start.resolve().perform()
                move_end.resolve().perform()

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        obj_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
