
class CutAction(ActionDesignatorDescription):
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_to_cut: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the cutting tool
            pickup_loc = CostmapLocation(target=self.object_to_cut, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_to_cut} with arm: {self.arm}")
            
            # navigate to cutting tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_to_cut, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location for performing cut
            cut_loc = CostmapLocation(target=self.object_to_cut, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                cut_pose = next(iter(cut_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
            
            # navigate to cutting location
            NavigateAction([cut_pose.pose]).resolve().perform()
            
            # determine coordinates of middle of object to be cut
            object_pose = self.object_to_cut.get_pose().resolve()
            object_x = object_pose.position.x
            object_y = object_pose.position.y
            object_z = object_pose.position.z
            object_length = object_pose.length
            object_width = object_pose.width
            object_height = object_pose.height
            middle_x = object_x
            middle_y = object_y
            middle_z = object_z + 0.5*object_height
            
            # perform cut
            if self.technique == "halving":
                # move tool to middle of object
                new_pose = Pose([middle_x, middle_y, middle_z])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        cut_pose = next(iter(cut_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                    NavigateAction([cut_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
                # move tool down to bottom of object
                new_pose = Pose([middle_x, middle_y, object_z])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        cut_pose = next(iter(cut_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                    NavigateAction([cut_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
                # move tool up to top of object
                new_pose = Pose([middle_x, middle_y, object_z+object_height])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        cut_pose = next(iter(cut_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                    NavigateAction([cut_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
            elif self.technique == "slicing":
                # determine number of slices to make
                num_slices = int(object_width/self.slice_thickness)
                # iterate over slices
                for i in range(num_slices):
                    # move tool to left side of object
                    new_pose = Pose([object_x+0.5*self.slice_thickness, object_y+i*self.slice_thickness, middle_z])
                    try:
                        MoveTCPMotion(new_pose).resolve().perform()
                    except IKError:
                        cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                        try:
                            cut_pose = next(iter(cut_loc))
                        except StopIteration:
                            raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                        NavigateAction([cut_pose.pose]).resolve().perform()
                        MoveTCPMotion(new_pose).resolve().perform()
                    # move tool to right side of object
                    new_pose = Pose([object_x+0.5*self.slice_thickness, object_y+(i+1)*self.slice_thickness, middle_z])
                    try:
                        MoveTCPMotion(new_pose).resolve().perform()
                    except IKError:
                        cut_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                        try:
                            cut_pose = next(iter(cut_loc))
                        except StopIteration:
                            raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
                        NavigateAction([cut_pose.pose]).resolve().perform()
                        MoveTCPMotion(new_pose).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
