
class CutAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        arms: List[str]
        grasps: List[str]
        techniques: List[str]
        slice_thicknesses: List[float]

        def perform(self) -> None:
            pass

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms, self.grasps, self.techniques, self.slice_thicknesses)
