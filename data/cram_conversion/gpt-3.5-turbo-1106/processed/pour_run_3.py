class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]
        @with_tree
        def perform(self) -> None:
            source_desig = self.object_source.resolve()
            container_desig = self.object_container.resolve()
            target_pose = Pose(position=[container_desig.pose.position[0], container_desig.pose.position[1], container_desig.pose.position[2] + 0.2], orientation=[0, 0, math.sin(math.pi/4), math.cos(math.pi/4)], frame=container_desig.pose.frame)
            approach_poses = []
            tilt_poses = []
            for arm in self.arms:
                if arm == Arms.LEFT:
                    approach_poses.append(Pose(position=[target_pose.position[0] - 0.1, target_pose.position[1], target_pose.position[2]], orientation=target_pose.orientation, frame=target_pose.frame))
                    tilt_poses.append(Pose(position=[target_pose.position[0], target_pose.position[1], target_pose.position[2]], orientation=[0, 0, math.sin(math.pi/2), math.cos(math.pi/2)], frame=target_pose.frame))
                elif arm == Arms.RIGHT:
                    approach_poses.append(Pose(position=[target_pose.position[0] + 0.1, target_pose.position[1], target_pose.position[2]], orientation=target_pose.orientation, frame=target_pose.frame))
                    tilt_poses.append(Pose(position=[target_pose.position[0], target_pose.position[1], target_pose.position[2]], orientation=[0, 0, math.sin(-math.pi/2), math.cos(-math.pi/2)], frame=target_pose.frame))
            move_source = MoveTCPMotion(target=source_desig.pose, arm=self.arms[0])
            move_container = MoveTCPMotion(target=target_pose, arm=self.arms[0])
            tilt_source = MoveTCPMotion(target=tilt_poses[0], arm=self.arms[0])
            tilt_container = MoveTCPMotion(target=tilt_poses[0], arm=self.arms[0])
            pour_duration = self.durations[0]
            move_source.resolve().perform()
            move_container.resolve().perform()
            time.sleep(1)  
            tilt_source.resolve().perform()
            tilt_container.resolve().perform()
            time.sleep(pour_duration)
            tilt_source.resolve().perform()  
            tilt_container.resolve().perform()  
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations)
