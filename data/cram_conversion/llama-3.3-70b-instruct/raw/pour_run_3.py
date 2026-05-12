class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            object_source = self.object_source_designator.resolve()
            object_container = self.object_container_designator.resolve()
            pose_source = object_source.pose
            pose_container = object_container.pose
            pose_pour = Pose(position=[pose_container.position[0], pose_container.position[1], pose_container.position[2] + 0.2], 
                             orientation=axis_angle_to_quaternion([0, 0, 1], math.pi/2), frame="map")
            MoveTCPMotion(pose_source, arm=self.arms[0]).resolve().perform()
            PickUpAction(object_source, self.arms, ["top"], resolver=None).resolve().perform()
            MoveTCPMotion(pose_pour, arm=self.arms[0]).resolve().perform()
            time.sleep(self.durations[0])
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
            PlaceAction(object_source, [pose_source], self.arms, resolver=None).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations

    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations)
