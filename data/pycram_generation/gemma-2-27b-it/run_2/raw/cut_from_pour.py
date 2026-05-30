class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            object_dimensions = self.object_designator.bullet_world_object.get_object_dimensions()
            if self.technique == "halving":
                cut_pose = Pose([pickup_pose.pose.position.x, pickup_pose.pose.position.y, pickup_pose.pose.position.z + object_dimensions[2]/2], [1, 0, 0, 1])
                MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                time.sleep(2)
            elif self.technique == "slicing":
                for i in range(int(object_dimensions[2]/self.slice_thickness)):
                    cut_pose = Pose([pickup_pose.pose.position.x, pickup_pose.pose.position.y, pickup_pose.pose.position.z + i*self.slice_thickness], [1, 0, 0, 1])
                    MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                    time.sleep(2)
            ParkArmsAction.Action