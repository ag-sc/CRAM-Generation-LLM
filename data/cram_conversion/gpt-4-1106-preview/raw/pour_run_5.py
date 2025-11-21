
import dataclasses
from typing import List, Union
from pycram.designator import ActionDesignatorDescription, ObjectDesignatorDescription
from pycram.task import with_tree
from pycram.pose import Pose
from pycram.designators.motion_designator import MoveTCPMotion
from pycram.robot_descriptions import robot_description
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer

class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            # Get the robot's current gripper state
            gripper_state = robot_description.get_gripper_state(self.arms[0])
            if gripper_state != "closed":
                raise Exception("Gripper is not holding an object.")

            # Get the pose of the source object
            source_pose = BulletWorld.robot.get_link_position(self.object_source.name, self.arms[0])

            # Get the pose of the target container
            container_pose = BulletWorld.robot.get_link_position(self.object_container.name)

            # Calculate the pouring pose 20 cm above the container's center
            pouring_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                                orientation=LocalTransformer.quaternion_from_euler(0, math.pi/2, 0))

            # Move the TCP to the pouring pose
            move_tcp_motion = MoveTCPMotion(target=pouring_pose, arm=self.arms[0])
            move_tcp_motion.resolve().perform()

            # Wait for the specified duration to pour the contents
            time.sleep(self.durations[0])

            # Return the TCP to the original pose of the source object
            move_tcp_motion = MoveTCPMotion(target=source_pose, arm=self.arms[0])
            move_tcp_motion.resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object],
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object],
                 arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms, self.durations)
