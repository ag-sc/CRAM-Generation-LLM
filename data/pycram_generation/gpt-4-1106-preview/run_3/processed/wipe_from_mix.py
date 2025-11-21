class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_description: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str
        @with_tree
        def perform(self) -> None:
            cloth = self.object_cloth_description.bullet_world_object
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                wipe_pose = wipe_location.copy()
                wipe_pose.pose.position.z += 0.05  
                start_x = wipe_pose.pose.position.x - length / 2
                start_y = wipe_pose.pose.position.y - width / 2
                end_x = start_x + length
                end_y = start_y + width
                y = start_y
                direction = 1
                while y <= end_y:
                    wipe_pose.pose.position.x = start_x
                    wipe_pose.pose.position.y = y
                    MoveTCPMotion(wipe_pose, self.arm).resolve().perform()
                    wipe_pose.pose.position.x = end_x
                    MoveTCPMotion(wipe_pose, self.arm).resolve().perform()
                    y += 0.1  
                    direction *= -1
                    start_x, end_x = end_x, start_x  
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
