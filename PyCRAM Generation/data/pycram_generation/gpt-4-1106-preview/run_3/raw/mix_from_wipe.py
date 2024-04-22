
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

            # find location to pick up the mixing tool
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl} with arm: {self.arm}")

            # navigate to mixing tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()

            # find location for performing mix
            mix_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                mix_pose = next(pose for pose in mix_loc)
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")

            # navigate to mixing location
            NavigateAction([mix_pose.pose]).resolve().perform()

            # perform mixing motion
            radius_increment = 0.01
            angle_increment = math.pi / 16
            current_radius = 0.0
            current_angle = 0.0
            bowl_center = self.object_bowl.resolve().pose.position
            while current_radius < 0.1:
                x_offset = current_radius * math.cos(current_angle)
                y_offset = current_radius * math.sin(current_angle)
                mix_pose = Pose([bowl_center.x + x_offset, bowl_center.y + y_offset, bowl_center.z])
                try:
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()
                except IKError:
                    raise ReachabilityFailure(f"Cannot reach the mixing pose: {mix_pose} with arm: {self.arm}")
                current_angle += angle_increment
                if current_angle >= 2 * math.pi:
                    current_angle -= 2 * math.pi
                    current_radius += radius_increment

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
