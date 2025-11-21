
class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            bowl_position = self.object_bowl.pose.position
            bowl_dimensions = self.object_bowl.bullet_world_object.get_object_dimensions()

            mix_radius = bowl_dimensions[0] / 2
            mix_height = bowl_position.z + bowl_dimensions[2] / 2
            mix_center = [bowl_position.x, bowl_position.y, mix_height]

            num_spirals = 3
            num_points_per_spiral = 10
            angle_step = (2 * math.pi) / num_points_per_spiral
            radius_step = mix_radius / (num_spirals * num_points_per_spiral)

            spiral_points = []
            current_radius = 0
            for spiral in range(num_spirals):
                for point in range(num_points_per_spiral):
                    angle = point * angle_step
                    x = mix_center[0] + current_radius * math.cos(angle)
                    y = mix_center[1] + current_radius * math.sin(angle)
                    z = mix_center[2]
                    spiral_points.append(Pose([x, y, z], [0, 0, 0, 1]))
                    current_radius += radius_step

            for point in spiral_points:
                move_tcp_motion = MoveTCPMotion(target=point, arm=self.arm)
                move_tcp_motion.resolve().perform()

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
