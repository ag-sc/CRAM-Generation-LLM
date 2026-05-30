class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator_description: ObjectDesignatorDescription.Object
        arms: List[str]
        grasps: List[str]
        techniques: List[str]
        slice_thicknesses: List[float]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_designator_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_designator_description} with arm: {self.arms[0]}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator_description, self.arms[0], self.grasps[0]).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            for i, technique in enumerate(self.techniques):
                if technique == 'halving':
                    cut_loc = CostmapLocation(target=self.object_designator_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
                    try:
                        cut_pose = next(pose for pose in cut_loc)
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_designator_description} with arm: {self.arms[0]}")
                    NavigateAction([cut_pose.pose]).resolve().perform()
                    MoveTCPMotion(cut_pose.pose).resolve().perform()
                elif technique == 'slicing':
                    object_width = self.object_designator_description.resolve().get_width()
                    for j in range(int(object_width / self.slice_thicknesses))
