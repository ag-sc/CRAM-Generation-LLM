
import dataclasses
from typing import List, Union
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription, ObjectPart
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion

class MixAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str

        def perform(self) -> None:
            if isinstance(self.object_bowl_desig, ObjectPart.Object):
                bowl_pose = self.object_bowl_desig.part_pose
            else:
                bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose()

            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            bowl_pose_in_gripper = lt.transform_pose(bowl_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))

            # move to bowl pose and close gripper
            MoveTCPMotion(bowl_pose, self.arm, allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()

            # perform mixing motion
            for _ in range(5):
                bowl_pose.pose.position.z += 0.05
                MoveTCPMotion(bowl_pose, self.arm, allow_gripper_collision=True).resolve().perform()
                bowl_pose.pose.position.z -= 0.05
                MoveTCPMotion(bowl_pose, self.arm, allow_gripper_collision=True).resolve().perform()

            # open gripper and move away from bowl
            MoveGripperMotion("open", self.arm).resolve().perform()
            bowl_pose.pose.position.x -= 0.1
            MoveTCPMotion(bowl_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if (isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) or isinstance(self.object_bowl_description, ObjectPart.Object)) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0])
