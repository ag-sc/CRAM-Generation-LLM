
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

            # find location to pick up the cloth object
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the cloth: {self.object_cloth} with arm: {self.arm}")

            # navigate to cloth object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            # calculate the start and end points for the zigzag pattern
            half_length = self.length / 2
            half_width = self.width / 2
            start_x = self.wipe_location.position.x - half_length
            start_y = self.wipe_location.position.y - half_width
            end_x = self.wipe_location.position.x + half_length
            end_y = self.wipe_location.position.y + half_width

            # create the zigzag pattern
            strip_gap = 0.1  # 10 cm gap between strips
            current_x = start_x
            direction = 1
            while current_x <= end_x:
                # move to the start of the strip
                strip_start_pose = Pose([current_x, start_y, self.wipe_location.position.z], self.wipe_location.orientation)
                MoveTCPMotion(strip_start_pose, self.arm).resolve().perform()

                # wipe the strip
                strip_end_pose = Pose([current_x, end_y, self.wipe_location.position.z], self.wipe_location.orientation)
                MoveTCPMotion(strip_end_pose, self.arm).resolve().perform()

                # move to the next strip
                current_x += strip_gap
                direction *= -1
                start_y, end_y = end_y, start_y  # reverse direction for the next strip

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
