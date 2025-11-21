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
                slicing_poses = [Pose(position=[object_pose.position[0], object_pose.position[1], object_pose.position[2]], orientation=object_pose.orientation)]
            elif self.technique == "slicing":
                object_size = bullet_world.get_object_dimensions(self.object_designator.name)
                num_slices = int(object_size[1] / self.slice_thickness)
                slicing_poses = []
                for i in range(num_slices):
                    offset = (i + 0.5) * self.slice_thickness - (object_size[1] / 2)
                    slicing_pose = Pose(position=[object_pose.position[0], object_pose.position[1] + offset, object_pose.position[2]], orientation=object_pose.orientation)
                    slicing_poses.append(slicing_pose)
            else:
                raise ValueError("Unknown cutting technique")
            for pose in slicing_poses:
                move_tcp_motion = MoveTCPMotion(target=pose, arm=self.arm)
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
