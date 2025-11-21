class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            mix_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                mix_pose = next(iter(mix_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")
            NavigateAction([mix_pose.pose]).resolve().perform()
            radius = 0.1
            angle_step = 0.1
            height = 0.05
            num_cycles = 5
            for cycle in range(num_cycles):
                for angle in np.arange(0, 2*math.pi, angle_step):
                    x = mix_pose.pose.position.x + radius * math.cos(angle)
                    y = mix_pose.pose.position.y + radius * math.sin(angle)
                    z = mix_pose.pose.position.z + cycle * height
                    new_pose = Pose([x, y, z])
                    try:
                        MoveTCPMotion(new_pose, self.arm).resolve().perform()
                    except IKError:
                        mix_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                        try:
                            mix_pose = next(iter(mix_loc))
                        except StopIteration:
                            raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")
                        NavigateAction([mix_pose.pose]).resolve().perform()
                        MoveTCPMotion(new_pose, self.arm).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
