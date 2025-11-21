class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose()
            tool_pose = Pose(position=[0.0, 0.0, 0.0], orientation=[0.0, 0.0, 0.0, 1.0], frame="tool_frame")
            MoveTCPMotion(tool_pose, self.arm).resolve().perform()
            for i in range(10):
                angle = i * 2 * math.pi / 10
                spiral_pose = Pose(position=[bowl_pose.position.x + 0.1 * math.cos(angle), bowl_pose.position.y + 0.1 * math.sin(angle), bowl_pose.position.z], orientation=[0.0, 0.0, 0.0, 1.0], frame="map")
                MoveTCPMotion(spiral_pose, self.arm).resolve().perform()
                time.sleep(0.5)
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if (isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) or isinstance(self.object_bowl_description, ObjectPart.Object)) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
