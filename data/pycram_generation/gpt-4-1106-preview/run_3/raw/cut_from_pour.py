
class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_target: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            # find location to pick up the cutting tool
            pickup_loc = CostmapLocation(target=self.object_target, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the tool: {self.object_target} with arm: {self.arm}")

            # navigate to cutting tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_target, self.arm, self.grasp).perform()

            # get the dimensions of the target object
            target_dimensions = self.object_target.bullet_world_object.get_object_dimensions()

            # determine the slicing motions based on the technique
            if self.technique == "halving":
                slice_poses = [Pose([pickup_pose.pose.position.x, pickup_pose.pose.position.y, pickup_pose.pose.position.z + target_dimensions[2] / 2], pickup_pose.pose.orientation)]
            elif self.technique == "slicing":
                num_slices = math.ceil(target_dimensions[1] / self.slice_thickness)
                slice_poses = []
                for i in range(num_slices):
                    slice_poses.append(Pose([pickup_pose.pose.position.x, pickup_pose.pose.position.y + i * self.slice_thickness, pickup_pose.pose.position.z + target_dimensions[2] / 2], pickup_pose.pose.orientation))
            else:
                raise ValueError(f"Unknown cutting technique: {self.technique}")

            # perform slicing motions
            for slice_pose in slice_poses:
                MoveTCPMotion(slice_pose, self.arm).resolve().perform()

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        target_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(target_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
