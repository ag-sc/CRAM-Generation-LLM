from pycram.designators.action_designator import ActionDesignatorDescription
from pycram.designators.object_designator import BelieveObject
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.pose import Pose
import math

class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            source_pose = self.object_source.resolve().get_pose()
            container_pose = self.object_container.resolve().get_pose()
            target_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2], orientation=container_pose.orientation)
            
            for arm in self.arms:
                MoveTCPMotion(target_pose, arm).resolve().perform()
                MoveGripperMotion('close', arm).resolve().perform()
                
                tilt_angle = math.radians(90)
                tilt_quaternion = axis_angle_to_quaternion([0, 1, 0], tilt_angle)
                target_pose.orientation = multiply_quaternions(target_pose.orientation, tilt_quaternion)
                MoveTCPMotion(target_pose, arm).resolve().perform()
                
                time.sleep(self.durations[0])
                
                MoveTCPMotion(target=source_pose, arm=arm).resolve().perform()
                MoveGripperMotion('open', arm).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container