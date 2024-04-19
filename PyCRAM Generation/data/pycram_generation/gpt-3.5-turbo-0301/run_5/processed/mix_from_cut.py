class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            object_bowl = self.object_bowl_designator.bullet_world_object
            oTm = object_bowl.get_pose()
            object_bowl_pose = object_bowl.local_transformer.transform_to_object_frame(oTm, object_bowl)
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            radius = 0.05
            height = 0.02
            num_circles = 3
            num_points_per_circle = 20
            angle_step = 2 * math.pi / num_points_per_circle
            z_step = height / num_points_per_circle
            mixing_trajectory = []
            for i in range(num_circles):
                for j in range(num_points_per_circle):
                    angle = i * angle_step + j * angle_step
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    z = i * z_step
                    mixing_trajectory.append([x, y, z])
            mixing_poses = []
            for point in mixing_trajectory:
                tmp_pose = object_bowl_pose.copy()
                tmp_pose.pose.position.x += point[0]
                tmp_pose.pose.position.y += point[1]
                tmp_pose.pose.position.z += point[2]
                sTm = object_bowl.local_transformer.transform_pose(tmp_pose, "map")
                mixing_poses.append(sTm)
            for pose in mixing_poses:
                ori = multiply_quaternions([pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w], grasp)
                adjusted_pose = pose.copy()
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
