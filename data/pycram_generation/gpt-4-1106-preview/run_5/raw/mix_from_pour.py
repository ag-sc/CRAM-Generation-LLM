
class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            # find location to pick up the mixing tool
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the mixing tool: {self.object_bowl} with arm: {self.arm}")

            # navigate to mixing tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()

            # get the dimensions of the bowl object
            bowl_dimensions = self.object_bowl.bullet_world_object.get_object_dimensions()

            # get the position of the bowl object
            bowl_position = self.object_bowl.pose.position

            # determine the initial pose for mixing inside the bowl
            mixing_pose = Pose([bowl_position.x, bowl_position.y, bowl_position.z + 0.1], [1, 0, 0, 1])

            # perform mixing motion
            for i in range(3):  # number of spirals
                for angle in np.linspace(0, 2 * math.pi, 36):  # 36 steps per spiral
                    radius = 0.05 * (i + 1)  # increasing radius for outward spiral
                    dx = radius * math.cos(angle)
                    dy = radius * math.sin(angle)
                    new_pose = Pose([mixing_pose.position.x + dx, mixing_pose.position.y + dy, mixing_pose.position.z], mixing_pose.orientation)
                    MoveTCPMotion(new_pose, self.arm).resolve().perform()

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
