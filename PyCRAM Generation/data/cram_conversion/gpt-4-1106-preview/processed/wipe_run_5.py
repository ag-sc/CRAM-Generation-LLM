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
            for arm in self.arms:
                for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                    num_strips = int(math.ceil(length / 0.1))
                    strip_length = width
                    for i in range(num_strips):
                        start_x = wipe_location.position[0] + i * 0.1
                        start_y = wipe_location.position[1]
                        end_x = start_x
                        end_y = start_y + strip_length
                        start_pose = Pose([start_x, start_y, wipe_location.position[2]], wipe_location.orientation, wipe_location.frame)
                        end_pose = Pose([end_x, end_y, wipe_location.position[2]], wipe_location.orientation, wipe_location.frame)
                        move_tcp_motion = MoveTCPMotion(start_pose, arm)
                        move_tcp_motion.resolve().perform()
                        move_tcp_motion = MoveTCPMotion(end_pose, arm)
                        move_tcp_motion.resolve().perform()
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
