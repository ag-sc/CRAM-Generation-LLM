class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @staticmethod
        def zigzag_points(center: np.ndarray, length: float, width: float, gap: float) -> List[Pose]:
            points = []
            x_start = center[0] - length / 2
            x_end = center[0] + length / 2
            y_start = center[1] - width / 2
            y_end = center[1] + width / 2
            y = y_start
            while y <= y_end:
                x = x_start
                while x <= x_end:
                    points.append(Pose([x, y, center[2]]))
                    x += gap
                y += gap
                if y > y_end:
                    break
                x = x_end
                while x >= x_start:
                    points.append(Pose([x, y, center[2]]))
                    x -= gap
                y += gap
            return points
        @staticmethod
        def wipe(arm: str, wipe_location: Pose) -> None:
            BulletWorld.current_bullet_world.add_vis_box(wipe_location, 0.01, 0.01, 0.01)
            MoveTCPMotion(wipe_location, arm).resolve().perform()
            BulletWorld.current_bullet_world.remove_vis_box()
        @with_tree
        def perform(self) -> None:
            cloth = self.object_cloth_designator.bullet_world_object
            for i, wipe_location in enumerate(self.wipe_locations):
                length = self.lengths[i]
                width = self.widths[i]
                points = self.zigzag_points(wipe_location.position, length, width, 0.1)
                for point in points:
                    point_in_map = cloth.local_transformer.transform_pose(point, "map")
                    self.wipe(self.arms[i], point_in_map)
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
