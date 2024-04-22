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
            bullet_world = BulletWorld.get_bullet_world()
            local_transformer = LocalTransformer.get_local_transformer()
            gripper = robot_description.i.get_gripper_for_arm(self.arms[0])
            cloth_pose = bullet_world.get_object_position(self.object_cloth.name)
            pick_cloth_motion = MoveTCPMotion(target=Pose(position=cloth_pose[0], orientation=cloth_pose[1]), arm=self.arms[0])
            pick_cloth_motion.resolve().perform()
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                num_strips = int(width / 0.1)
                strip_length = length / num_strips
                for i in range(num_strips):
                    start_x = wipe_location.position[0] - (length / 2) + (i * strip_length)
                    end_x = start_x + strip_length
                    start_pose = Pose(position=[start_x, wipe_location.position[1], wipe_location.position[2]], orientation=wipe_location.orientation)
                    end_pose = Pose(position=[end_x, wipe_location.position[1], wipe_location.position[2]], orientation=wipe_location.orientation)
                    move_to_start = MoveTCPMotion(target=start_pose, arm=self.arms[0])
                    move_to_start.resolve().perform()
                    move_to_end = MoveTCPMotion(target=end_pose, arm=self.arms[0])
                    move_to_end.resolve().perform()
            release_cloth_motion = MoveTCPMotion(target=Pose(position=cloth_pose[0], orientation=cloth_pose[1]), arm=self.arms[0], allow_gripper_collision=True)
            release_cloth_motion.resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth, self.wipe_locations, self.lengths, self.widths, self.arms)
