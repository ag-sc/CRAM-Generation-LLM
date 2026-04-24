class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            pickup_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_designator} with arm: {self.arm}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            object_dimensions = self.object_designator.bullet_world_object.get_object_dimensions()

            if self.technique == 'halving':
                cut_pose = Pose([pickup_pose.pose.position.x, pickup_pose.pose.position.y, pickup_pose.pose.position.z + object_dimensions[2] / 2], [1, 0, 0, 1])
                MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                time.sleep(1)
                MoveTCPMotion(Pose([cut_pose.position.x, cut_pose.position.y, cut_pose.position.z - object_dimensions[2]], [1, 0, 0, 1]), self.arm).resolve().perform()
            elif self.technique =='slicing':
                num_slices = int(object_dimensions[1] / self.slice_thickness)
                for i in range(num_slices):
                    cut_pose = Pose([pickup_pose.pose.position.x, pickup_pose.pose.position.y + i * self.slice_thickness, pickup_pose.pose.position.z + object_dimensions[2] / 2], [1, 0, 0, 1])
                    MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                    time.sleep(1)
                    MoveTCPMotion(Pose([cut_pose.position.x, cut_pose.position.y, cut_pose.position.z - object_dimensions[2]], [1, 0, 0, 1]), self.arm).resolve().perform()

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms
        self.grasps = grasps
        self.techniques = techniques
        self.slice_thicknesses = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
