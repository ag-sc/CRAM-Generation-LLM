
class TransportAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        target_locations: List[Pose]

        @with_tree
        def perform(self) -> None:
            PickUpAction(self.object_desig, [self.arm], ["grasp"]).resolve().perform()
            NavigateAction(self.target_locations).resolve().perform()
            PlaceAction(self.object_desig, self.target_locations, [self.arm]).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations

    def ground(self) -> Action:
        object_desig = self.object_description if (isinstance(self.object_description, ObjectDesignatorDescription.Object) or isinstance(self.object_description, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations)
