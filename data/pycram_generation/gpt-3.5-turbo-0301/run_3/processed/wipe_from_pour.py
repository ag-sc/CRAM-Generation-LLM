class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth} with arm: {self.arms[0]}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arms, "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            cloth_dimensions = self.object_cloth.bullet_world_object.get_object_dimensions()
            for i, loc in enumerate(self.wipe_locations):
                num_strips_length = math.ceil(self.lengths[i] / 0.1)
                num_strips_width = math.ceil(self.widths[i] / 0.1)
                start_pos = Pose([loc.position[0] - 0.5*self.lengths[i], loc.position[1] - 0.5*self.widths[i], loc.position[2]], [1, 0, 0, 1])
                for j in range(num_strips_length):
                    strip_start_pos = Pose([start_pos.position[0] + j*0.1, start_pos.position[1], start_pos.position[2]], [1, 0, 0, 1])
                    if j % 2 == 0:
                        strip_direction = [0, 1, 0]
                    else:
                        strip_direction = [0, -1, 0]
                    for k in range(num_strips_width):
                        wipe_start_pos = Pose([strip_start_pos.position[0], strip_start_pos.position[1] + k*0.1, strip_start_pos.position[2]], [1, 0, 0, 1])
                        if k % 2 == 0:
                            wipe_direction = [1, 0, 0]
                        else:
                            wipe_direction = [-1, 0, 0]
                        wipe_end_pos = Pose([wipe_start_pos.position[0] + wipe_direction[0]*self.lengths[i], wipe_start_pos.position[1] + wipe_direction[1]*self.widths[i], wipe_start_pos.position[2] + cloth_dimensions[2]], [1, 0, 0, 1])
                        NavigateAction([wipe_start_pos]).resolve().perform()
                        MoveTCPMotion(wipe_end_pos, self.arms[0]).resolve().perform()
                        MoveTCPMotion(wipe_start_pos, self.arms[0]).resolve().perform()
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
