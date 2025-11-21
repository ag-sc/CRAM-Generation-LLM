class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_bowl_designator.data_copy()
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            object_bowl = self.object_bowl_designator.bullet_world_object
            oTm = object_bowl.get_pose()
            object_bowl_pose = object_bowl.local_transformer.transform_to_object_frame(oTm, object_bowl)
            bowl_radius = max(object_bowl.get_object_dimensions()) / 2
            num_steps = 100
            for i in range(num_steps):
                r = i / num_steps * bowl_radius
                theta = i / num_steps * 2 * math.pi
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                tmp_pose = object_bowl_pose.copy()
                tmp_pose.pose.position.x = x
                tmp_pose.pose.position.y = y
                sTm = object_bowl.local_transformer.transform_pose(tmp_pose, "map")
                ori = multiply_quaternions([sTm.orientation.x, sTm.orientation.y, sTm.orientation.z, sTm.orientation.w], grasp)
                adjusted_pose = sTm.copy()
                adjusted_pose.orientation.x = ori[0]
                adjusted_pose.orientation.y = ori[1]
                adjusted_pose.orientation.z = ori[2]
                adjusted_pose.orientation.w = ori[3]
                MoveTCPMotion(adjusted_pose, self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
