class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        @with_tree
        def perform(self) -> None:
            cloth = self.object_cloth_designator.bullet_world_object
            cloth_pose = cloth.get_pose()
            wipe_center_pose = self.wipe_location
            start_x = wipe_center_pose.pose.position.x - self.length / 2
            end_x = wipe_center_pose.pose.position.x + self.length / 2
            start_y = wipe_center_pose.pose.position.y - self.width / 2
            end_y = wipe_center_pose.pose.position.y + self.width / 2
            gap = 0.1  
            current_y = start_y
            direction = 1  
            while current_y <= end_y:
                strip_start_pose = Pose([start_x, current_y, cloth_pose.pose.position.z], wipe_center_pose.pose.orientation, frame="map")
                MoveTCPMotion(strip_start_pose, self.arm).resolve().perform()
                strip_end_x = end_x if direction == 1 else start_x
                strip_end_pose = Pose([strip_end_x, current_y, cloth_pose.pose.position.z], wipe_center_pose.pose.orientation, frame="map")
                MoveTCPMotion(strip_end_pose, self.arm).resolve().perform()
                current_y += gap
                direction *= -1  
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
