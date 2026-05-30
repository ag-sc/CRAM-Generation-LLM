class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth.data_copy()
            cloth = self.object_cloth.bullet_world_object
            for i, location in enumerate(self.wipe_locations):
                for j in range(int(self.lengths[i] / 0.1)):
                    x_offset = j * 0.1
                    if j % 2 == 0:
                        start_pose = location.copy()
                        start_pose.pose.position.x += x_offset
                        start_pose.pose.position.y -= self.widths[i] / 2
                        end_pose = start_pose.copy()
                        end_pose.pose.position.y += self.widths[i]
                    else:
                        start_pose = location.copy()
                        start_pose.pose.position.x += x_offset
                        start_pose.pose.position.y += self.widths[i] / 2
                        end_pose = start_pose.copy()
                        end_pose.pose.position.y -= self.widths[i]
                    MoveTCPMotion(start_pose, self.arm).resolve().perform()
                    MoveTCPMotion(end_pose, self.arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] =
