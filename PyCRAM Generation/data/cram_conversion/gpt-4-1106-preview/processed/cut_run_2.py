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
            bullet_world = BulletWorld.get_bullet_world()
            local_transformer = LocalTransformer.get_local_transformer()
            robot = robot_description.get_robot_description()
            object_pose = bullet_world.get_object_pose(self.object_designator.name)
            if self.technique == "halving":
                slicing_poses = [Pose(position=[object_pose.position[0], object_pose.position[1], object_pose.position[2] + 0.1], orientation=object_pose.orientation)]
            elif self.technique == "slicing":
                slicing_poses = []
                object_width = bullet_world.get_object_dimensions(self.object_designator.name)[0]
                num_slices = int(object_width / self.slice_thickness)
                for i in range(num_slices):
                    slice_offset = (i + 0.5) * self.slice_thickness - (object_width / 2)
                    slicing_poses.append(Pose(position=[object_pose.position[0] + slice_offset, object_pose.position[1], object_pose.position[2] + 0.1], orientation=object_pose.orientation))
            else:
                raise ValueError("Unknown cutting technique: " + self.technique)
            for pose in slicing_poses:
                pose_in_base = local_transformer.transform_pose(pose, "base_footprint")
                move_tcp_motion = MoveTCPMotion(target=pose_in_base, arm=self.arm)
                move_tcp_motion.resolve().perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
