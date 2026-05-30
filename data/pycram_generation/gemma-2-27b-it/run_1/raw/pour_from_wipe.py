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
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            container_loc = CostmapLocation(target=self.object_container, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                container_pose = next(iter(container_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to pour into the container: {self.object_container} with arm: {self.arm}")
            NavigateAction([container_pose.pose]).resolve().perform()
            target_pose = Pose([container_pose.pose.position.x, container_pose.pose.position.y, container_pose.pose.position.z + 0.2])
            MoveTCPMotion(target_pose, self.arm).resolve().perform()
            
            # Tilt the source object at a 90° angle
            # ... (Implementation for tilting the object)
            
            time.sleep(self.duration)
            
            # Return the source object to its original orientation
            # ... (Implementation for returning the object to its original orientation)
            
            ParkArmsAction.