
class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose() if isinstance(self.object_bowl_desig, ObjectDesignatorDescription.Object) else self.object_bowl_desig.part_pose
            lt = LocalTransformer()
            tool_frame = robot_description.get_tool_frame(self.arm)
            bowl_pose_in_tool = lt.transform_pose(bowl_pose, BulletWorld.robot.get_link_tf_frame(tool_frame))

            # Define the parameters for the mixing motion
            radius_increment = 0.005
            angle_increment = math.radians(10)
            current_radius = 0.05
            current_angle = 0.0
            num_spirals = 3
            height_offset = 0.1

            # Perform the mixing motion
            for _ in range(num_spirals):
                while current_radius < 0.1:
                    # Calculate the next pose in the spiral
                    x_offset = current_radius * math.cos(current_angle)
                    y_offset = current_radius * math.sin(current_angle)
                    next_pose = bowl_pose_in_tool.copy()
                    next_pose.pose.position.x += x_offset
                    next_pose.pose.position.y += y_offset
                    next_pose.pose.position.z += height_offset

                    # Move to the next pose
                    MoveTCPMotion(next_pose, self.arm).resolve().perform()

                    # Update the spiral parameters
                    current_angle += angle_increment
                    current_radius += radius_increment

            # Return to the initial pose
            MoveTCPMotion(bowl_pose_in_tool, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
