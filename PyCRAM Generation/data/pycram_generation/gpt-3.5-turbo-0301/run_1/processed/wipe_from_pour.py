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
                start_x = loc.position[0] - 0.5*self.lengths[i]
                end_x = loc.position[0] + 0.5*self.lengths[i]
                start_y = loc.position[1] - 0.5*self.widths[i]
                end_y = loc.position[1] + 0.5*self.widths[i]
                num_strips = math.ceil(self.widths[i]/0.1)
                direction = 1 if i%2 == 0 else -1
                for j in range(num_strips):
                    strip_start_y = start_y + j*0.1*direction
                    strip_end_y = strip_start_y + 0.1*direction
                    wipe_pose = Pose([start_x, (strip_start_y+strip_end_y)/2, loc.position[2]+0.1], [1, 0, 0, 1])
                    wipe_loc = CostmapLocation(target=wipe_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
                    try:
                        wipe_pose = next(iter(wipe_loc))
                    except StopIteration:
                        raise ReachabilityFailure(f"Found no pose for the robot to wipe at location: {wipe_pose} with arm: {self.arms[0]}")
                    NavigateAction([wipe_pose.pose]).resolve().perform()
                    MoveTCPMotion(wipe_pose, self.arms[0]).resolve().perform()
                    time.sleep(0.5)
                direction *= -1
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
        return self.Action(cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
