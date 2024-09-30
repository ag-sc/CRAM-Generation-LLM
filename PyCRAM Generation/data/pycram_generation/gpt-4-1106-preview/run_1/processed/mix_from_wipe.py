class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()
            mix_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                mix_pose = next(pose for pose in mix_loc)
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")
            NavigateAction([mix_pose.pose]).resolve().perform()
            radius = 0.05  
            angle_step = 10  
            radius_increment = 0.005  
            num_turns = 3  
            for turn in range(num_turns):
                for angle in range(0, 360, angle_step):
                    rad_angle = math.radians(angle)
                    offset_x = radius * math.cos(rad_angle)
                    offset_y = radius * math.sin(rad_angle)
                    new_pose = Pose([mix_pose.pose.position.x + offset_x, mix_pose.pose.position.y + offset_y, mix_pose.pose.position.z])
                    try:
                        MoveTCPMotion(new_pose, self.arm).resolve().perform()
                    except IKError:
                        raise ReachabilityFailure(f"Cannot reach the position for mixing at angle {angle} and radius {radius}")
                radius += radius_increment
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
