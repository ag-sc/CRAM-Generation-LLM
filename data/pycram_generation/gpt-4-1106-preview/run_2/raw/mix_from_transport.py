
class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            tool_desig = ObjectPart(names=["mixing_tool"], part_of=robot_desig.resolve(), type="Tool")
            bowl_pose_desig = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)

            # Find a pose to perform the mixing action
            bowl_pose = next(bowl_pose_desig, None)
            if not bowl_pose:
                raise ObjectUndeliverable(f"No pose found to perform mixing at the bowl: {self.object_bowl_designator}")

            # Navigate to the bowl and perform the mixing action
            NavigateAction([bowl_pose.pose]).resolve().perform()
            PickUpAction.Action(tool_desig, [self.arm], [self.grasp]).perform()

            # Define the mixing motion parameters
            radius_increment = 0.01  # Increment the radius by 1 cm per revolution
            angle_increment = math.pi / 8  # Increment the angle by 22.5 degrees per step
            current_radius = 0.05  # Start with a 5 cm radius
            current_angle = 0

            # Perform the mixing motion
            while current_radius <= 0.15:  # Continue until reaching a 15 cm radius
                x_offset = current_radius * math.cos(current_angle)
                y_offset = current_radius * math.sin(current_angle)
                mixing_pose = Pose(position=[bowl_pose.pose.position[0] + x_offset, bowl_pose.pose.position[1] + y_offset, bowl_pose.pose.position[2]],
                                   orientation=bowl_pose.pose.orientation,
                                   frame=bowl_pose.pose.frame)
                MoveTCPMotion.Action(mixing_pose, self.arm).perform()
                current_angle += angle_increment
                if current_angle >= 2 * math.pi:
                    current_angle -= 2 * math.pi
                    current_radius += radius_increment

            # Place the tool back
            PlaceAction.Action(tool_desig, [bowl_pose.pose], [self.arm]).perform()
            ParkArmsAction.Action([self.arm]).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        obj_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_bowl_desig, self.arms[0], self.grasps[0])
