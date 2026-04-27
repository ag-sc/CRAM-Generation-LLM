from pycram.designators.action_designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription
from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer
from pycram.pose import Pose
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion

class CutAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            bullet_world = BulletWorld()
            object_pose = self.object_designator.resolve().get_pose()
            if self.technique == 'halving':
                cut_pose = Pose(position=[object_pose.position[0], object_pose.position[1], object_pose.position[2] + self.slice_thickness/2], 
                              orientation=object_pose.orientation, frame='map')
                MoveTCPMotion(target=cut_pose, arm=self.arm).resolve().perform()
                MoveGripperMotion(motion='close', gripper=self.grasp).resolve().perform()
                MoveTCPMotion(target=Pose(position=[object_pose.position[0], object_pose.position[1], object_pose.position[2] - self.slice_thickness/2], 
                              orientation=object_pose.orientation, frame='map'), arm=self.arm).resolve().perform()
                MoveGripperMotion(motion='open', gripper=self.grasp).resolve().perform()
            elif self.technique =='slicing':
                for i in range(int((object_pose.position[2] - self.slice_thickness) / self.slice_thickness)):
                    cut_pose = Pose(position=[object_pose.position[0], object_pose.position[1], object_pose.position[2] - i * self.slice_thickness], 
                                  orientation=object_pose.orientation, frame='map')
                    MoveTCPMotion(target=cut_pose, arm=self.arm).resolve().perform()
                    MoveGripperMotion(motion='close', gripper=self.grasp).resolve().perform()
                    MoveTCPMotion(target=Pose(position=[object_pose.position[0], object_pose.position[1], object_pose.position[2] - (i+1) * self.slice_thickness], 
                                  orientation=object_pose.orientation, frame='map'), arm=self.arm).resolve().perform()
                    MoveGripperMotion(motion='open', gripper=self.grasp).resolve().perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms
        self.grasps = grasps
        self.techniques = techniques
        self.slice_thicknesses = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
