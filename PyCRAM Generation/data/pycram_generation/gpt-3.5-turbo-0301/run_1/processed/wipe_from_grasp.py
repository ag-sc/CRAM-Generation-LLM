class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            if isinstance(self.object_cloth_desig, ObjectPart.Object):
                cloth_pose = self.object_cloth_desig.part_pose
            else:
                cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arms[0])
            cloth_pose_in_gripper = lt.transform_pose(cloth_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            PickUpAction(self.object_cloth_desig, self.arms, ["pinch"]).resolve().perform()
            for i, loc in enumerate(self.wipe_locations):
                MoveTCPMotion(loc, self.arms[0]).resolve().perform()
                length = self.lengths[i]
                width = self.widths[i]
                gap = 0.1
                num_strips = math.ceil(width / gap)
                for j in range(num_strips):
                    if j % 2 == 0:
                        start = Pose([0, j * gap, 0], [0, 0, 0, 1])
                        end = Pose([length, j * gap, 0], [0, 0, 0, 1])
                    else:
                        start = Pose([length, (j + 1) * gap, 0], [0, 0, 0, 1])
                        end = Pose([0, (j + 1) * gap, 0], [0, 0, 0, 1])
                    MoveTCPMotion(lt.transform_pose(start, loc.frame), self.arms[0]).resolve().perform()
                    MoveTCPMotion(lt.transform_pose(end, loc.frame), self.arms[0]).resolve().perform()
            PlaceAction(self.object_cloth_desig, self.wipe_locations, self.arms).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
