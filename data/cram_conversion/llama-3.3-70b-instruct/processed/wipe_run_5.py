class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        @with_tree
        def perform(self) -> None:
            MoveGripperMotion('open', 'left_gripper').resolve().perform()
            PickUpAction(self.object_cloth_designator, ['left'], ['scrubbing']).resolve().perform()
            poses = []
            for i in range(int(self.length // 0.1)):
                pose = Pose(position=[self.wipe_location.position[0], self.wipe_location.position[1] + i * 0.1, self.wipe_location.position[2]], 
                            orientation=self.wipe_location.orientation, 
                            frame=self.wipe_location.frame)
                if i % 2 == 0:
                    pose.position[0] -= self.width / 2
                else:
                    pose.position[0] += self.width / 2
                poses.append(pose)
            MoveTCPMotion(poses[0], self.arm).resolve().perform()
            for pose in poses[1:]:
                MoveTCPMotion(pose, self.arm).resolve().perform()
            MoveGripperMotion('close', 'left_gripper').resolve().perform()
            PlaceAction(self.object_cloth_designator, [Pose(position=[0, 0, 0], orientation=[0, 0, 0, 1], frame='map')], ['left']).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
