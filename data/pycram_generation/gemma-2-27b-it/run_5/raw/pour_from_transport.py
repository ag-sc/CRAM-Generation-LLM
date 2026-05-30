class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_source, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            container_loc = CostmapLocation(target=self.object_container, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            NavigateAction([container_loc.pose]).resolve().perform()

            source_pose = self.object_source.resolve().pose
            container_pose = self.object_container.resolve().pose
            target_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2])
            
            MoveTCPMotion(target=target_pose, arm=self.arm).perform()
            
            tilt_angle = math.radians(90)
            tilt_quaternion = axis_angle_to_quaternion([0, 1, 0], tilt_angle)
            
            current_orientation = source_pose.orientation
            target_orientation = multiply_quaternions(current_orientation, tilt_quaternion)