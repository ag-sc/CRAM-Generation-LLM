
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            source = self.object_source.resolve()
            container = self.object_container.resolve()
            target_pose = Pose(position=[container.pose.position[0], container.pose.position[1], container.pose.position[2] + 0.2], orientation=[0, 0, math.sin(math.pi/4), math.cos(math.pi/4)], frame=container.pose.frame)
            approach_poses = []
            tilt_poses = []
            for arm in self.arms:
                if arm == "left":
                    approach_poses.append(Pose(position=[source.pose.position[0] - 0.1, source.pose.position[1], source.pose.position[2]], orientation=source.pose.orientation, frame=source.pose.frame))
                    tilt_poses.append(Pose(position=[source.pose.position[0], source.pose.position[1], source.pose.position[2]], orientation=[0, 0, math.sin(math.pi/2), math.cos(math.pi/2)], frame=source.pose.frame))
                elif arm == "right":
                    approach_poses.append(Pose(position=[source.pose.position[0] + 0.1, source.pose.position[1], source.pose.position[2]], orientation=source.pose.orientation, frame=source.pose.frame))
                    tilt_poses.append(Pose(position=[source.pose.position[0], source.pose.position[1], source.pose.position[2]], orientation=[0, 0, math.sin(math.pi/2), math.cos(math.pi/2)], frame=source.pose.frame))
            move_source = MoveTCPMotion(target=source.pose, arm=None)
            move_container = MoveTCPMotion(target=target_pose, arm=None)
            tilt_source = MoveTCPMotion(target=tilt_poses[0], arm=self.arms[0])
            pour_duration = self.durations[0]
            # perform the actions
            move_source.resolve().perform()
            move_container.resolve().perform()
            tilt_source.resolve().perform()
            time.sleep(pour_duration)
            tilt_source = MoveTCPMotion(target=source.pose, arm=self.arms[0])
            tilt_source.resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms, self.durations)
