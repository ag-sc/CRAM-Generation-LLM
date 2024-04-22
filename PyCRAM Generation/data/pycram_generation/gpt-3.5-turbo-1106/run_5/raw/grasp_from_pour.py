
class GraspAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        arm: str
        
        def perform(self):
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_pose = MoveTCPMotion(Pose(position=[self.object.pose.position.x-0.1, self.object.pose.position.y, self.object.pose.position.z], orientation=[1, 0, 0, 1]), self.arm)
            pre_grasp_pose.resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            grasp_pose = MoveTCPMotion(self.object.pose, self.arm)
            grasp_pose.resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
