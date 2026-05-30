class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_description: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth_description} with arm: {self.arm}")

            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_description, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            for i, wipe_location in enumerate(self.wipe_locations):
                place_loc = CostmapLocation(target=wipe_location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
                NavigateAction([place_loc.pose]).resolve().perform()
                for j in range(int(self.lengths[i] / 0.1)):
                    MoveTCPMotion(target=Pose(position=[place_loc.pose.position[0] + j * 0.1, place_loc.pose.position[1], place_loc.pose.position[2]]), arm=self.arm).perform()
                for j in range(int(self.widths[i] / 0.1)):
                    MoveTCPMotion(target=Pose(position=[place_loc.pose.position[0] + self.lengths[i], place_loc.pose.position[1] +