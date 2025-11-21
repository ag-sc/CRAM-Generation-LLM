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
            ParkArmsAction.Action(Arms.BOTH).perform()
            bowl_dimensions = self.object_bowl.bullet_world_object.get_object_dimensions()
            bowl_position = self.object_bowl.pose.position
            tool_pose = Pose([bowl_position.x, bowl_position.y, bowl_position.z+0.2], [1, 0, 0, 1])
            mix_loc = CostmapLocation(target=tool_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                mix_pose = next(iter(mix_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to mix in the bowl: {self.object_bowl} with arm: {self.arm}")
            NavigateAction([mix_pose.pose]).resolve().perform()
            for i in range(10):
                MoveTCPMotion(Pose([bowl_position.x + 0.2 * math.cos(i * math.pi / 5), bowl_position.y + 0.2 * math.sin(i * math.pi / 5), bowl_position.z + 0.2], [1, 0, 0, 1]), self.arm).resolve().perform()
                time.sleep(0.5)
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
