class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        def perform(self) -> None:
            self.object_at_execution = self.object_bowl_designator.data_copy()
            grasp_orientation = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            bowl = self.object_bowl_designator.bullet_world_object
            bowl_dim = bowl.get_object_dimensions()
            bowl_pose = bowl.local_transformer.transform_to_object_frame(bowl.get_pose(), bowl)
            radius = min(bowl_dim[0], bowl_dim[1]) / 2
            num_spirals = 3
            num_points_per_spiral = 10
            height_offset = bowl_dim[2] / 2
            for spiral in range(num_spirals):
                for point in range(num_points_per_spiral):
                    angle = (2 * math.pi / num_points_per_spiral) * point
                    r = radius * ((spiral * num_points_per_spiral + point) / (num_spirals * num_points_per_spiral))
                    x = r * math.cos(angle)
                    y = r * math.sin(angle)
                    mix_pose = bowl_pose.copy()
                    mix_pose.pose.position.x += x
                    mix_pose.pose.position.y += y
                    mix_pose.pose.position.z += height_offset
                    mix_pose.orientation = multiply_quaternions(
                        [mix_pose.orientation.x, mix_pose.orientation.y, mix_pose.orientation.z, mix_pose.orientation.w],
                        grasp_orientation
                    )
                    BulletWorld.current_bullet_world.add_vis_axis(mix_pose)
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()
                    BulletWorld.current_bullet_world.remove_vis_axis()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
