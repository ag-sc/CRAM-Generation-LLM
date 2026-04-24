class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            object = self.object_bowl_designator.bullet_world_object
            obj_dim = object.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            def generate_spiral(pose, upward_increment, radial_increment, angle_increment, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                spiral_poses = []

                for t in range(2 * steps):
                    tmp_pose = pose.copy()

                    r = radial_increment * t
                    a = angle_increment * t
                    h = upward_increment * t

                    x = x_start + r * math.cos(a)
                    y = y_start + r * math.sin(a)
                    z = z_start + h

                    tmp_pose.pose.position.x += x
                    tmp_pose.pose.position.y += y
                    tmp_pose.pose.position.z += z

                    spiralTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    spiral_poses.append(spiralTm)
                    BulletWorld.current_bullet_world.add_vis_axis(spiralTm)

                return spiral_poses

            spiral_poses = generate_spiral(object_pose, 0.001, 0.0035, math.radians(30), 10)

            BulletWorld.current_bullet_world.remove_vis_axis()
            for spiral_pose in spiral_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([spiral_pose.orientation.x, spiral_pose.orientation.y,
                                            spiral_pose.orientation.z, spiral_pose.orientation.w], oriR)
                adjusted_slice_pose = spiral_pose.copy()
                adjusted_slice_pose.orientation.x = ori[0]
                adjusted_slice_pose.orientation.y = ori[1]
                adjusted_slice_pose.orientation.z = ori[2]
                adjusted_slice_pose.orientation.w = ori[3]

                lift_pose = adjusted_slice_pose.copy()
                lift_pose.pose.position.z += (obj_height + 0.08)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()

        def to_sql(self) -> ORMMixingAction:
            return ORMMixingAction(self.arm, self.grasp)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super(MixAction, self).__init__(resolver)
        self.object_bowl_designator: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        return self.Action(self.object_bowl_designator, self.arms[0], self.grasps[0])
