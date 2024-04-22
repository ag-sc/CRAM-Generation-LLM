
class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            tool_desig = ObjectPart(names=["mixing_tool"], part_of=self.object_bowl_designator)
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_tool_loc = CostmapLocation(target=tool_desig, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_tool_pose = next(pickup_tool_loc, None)
            if not pickup_tool_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the tool: {tool_desig} with arm: {self.arm}")

            NavigateAction([pickup_tool_pose.pose]).resolve().perform()
            PickUpAction.Action(tool_desig, self.arm, self.grasp).perform()

            bowl_loc = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            bowl_pose = next(bowl_loc, None)
            if not bowl_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to perform mixing at the bowl: {self.object_bowl_designator} with arm: {self.arm}")

            NavigateAction([bowl_pose.pose]).resolve().perform()

            # Perform mixing motion
            # This is a placeholder for the actual mixing motion, which would involve
            # a series of MoveTCPMotion actions to create the counterclockwise, outward spiraling motion.
            # The actual implementation of the mixing motion would depend on the robot's kinematics and control capabilities.

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        obj_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_bowl_desig, self.arms[0], self.grasps[0])
