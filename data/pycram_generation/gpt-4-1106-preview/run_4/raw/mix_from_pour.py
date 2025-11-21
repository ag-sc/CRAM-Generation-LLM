
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
            mix_pose = Pose([bowl_position.x, bowl_position.y, bowl_position.z + 0.1], [1, 0, 0, 1])

            # perform mixing motion
            for i in range(3):  # number of spirals
                for angle in np.linspace(0, 2 * math.pi, num=20):
                    # calculate the offset for the spiral motion
                    offset = 0.05 * i  # outward spiral step
                    dx = offset * math.cos(angle)
                    dy = offset * math.sin(angle)
                    # update the mix pose
                    mix_pose.position = [bowl_position.x + dx, bowl_position.y + dy, mix_pose.position[2]]
                    # move to the next position in the spiral
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()

            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
