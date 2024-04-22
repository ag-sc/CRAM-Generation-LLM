
class WipeAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_cloth_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]

        @with_tree
        def perform(self) -> None:
            cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()

            for pose, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                for x in np.arange(-length/2, length/2, 0.1):
                    pose.pose.position.x = x
                    for y in np.arange(-width/2, width/2, 0.1):
                        pose.pose.position.y = y
                        target_pose = lt.transform_pose(pose, cloth_pose.frame)
                        MoveTCPMotion(target_pose, self.arms[0]).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
