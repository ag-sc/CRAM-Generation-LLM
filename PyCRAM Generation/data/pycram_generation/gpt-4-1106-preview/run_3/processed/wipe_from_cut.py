class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_description: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        gap: float = 0.1
        @with_tree
        def perform(self) -> None:
            object_cloth = self.object_cloth_description.bullet_world_object
            cloth_pose = object_cloth.get_pose()
            start_x = self.wipe_location.pose.position.x - self.length / 2
            start_y = self.wipe_location.pose.position.y - self.width / 2
            end_x = start_x + self.length
            end_y = start_y + self.width
            current_x = start_x
            current_y = start_y
            direction = 1
            while current_x <= end_x:
                target_pose = Pose([current_x, current_y, cloth_pose.pose.position.z], self.wipe_location.pose.orientation, self.wipe_location.frame)
                MoveTCPMotion(target_pose, self.arm).resolve().perform()
                current_y += direction * self.width
                if current_y > end_y or current_y < start_y:
                    direction *= -1
                    current_y = end_y if direction < 0 else start_y
                    current_x += self.gap
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
