class WipeAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth.data_copy()
            cloth = self.object_cloth.bullet_world_object
            def generate_wipe_trajectory(pose, length, width, gap):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                wipe_poses = []
                for i in range(len(length)):
                    for j in range(len(width)):
                        x = x_start - length[i] / 2
                        y = y_start - width[j] / 2
                        z = z_start
                        for k in range(int(length[i] / gap)):
                            x += gap
                            wipe_poses.append(Pose([x, y, z], pose.orientation))
                        y += gap
                        for k in range(int(width[j] / gap)):
                            y += gap
                            wipe_poses.append(Pose([x, y, z], pose.orientation))
                        x -= gap
                        for k in range(int(length[i] / gap)):
                            x -= gap
                            wipe_poses.append(Pose([x, y, z], pose.orientation))
                        y -= gap
                        for k in range(int(width[j] / gap)):
                            y -= gap
                            wipe_poses.append(Pose([x, y, z], pose.orientation))
                return wipe_poses
            wipe_poses = generate_wipe_trajectory(self.wipe_locations[0], self.lengths, self.widths, 0.1)
            for wipe_pose in wipe_poses:
                MoveTCPMotion(wipe_pose, self.arms[0]).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
