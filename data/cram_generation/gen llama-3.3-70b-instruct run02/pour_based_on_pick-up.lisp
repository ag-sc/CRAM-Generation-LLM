(<- (desig:action-grounding?action-designator (pour?current-container-desig?target-container-desig 
                                                         ?arm?gripper-opening?effort?grasp 
                                                         ?pouring-poses?left-pouring-poses 
                                                         ?right-pouring-poses?left-target-poses 
                                                         ?right-target-poses))
    (spec:property?action-designator (:type :pouring))
    (spec:property?action-designator (:object?container-designator))
    (desig:current-designator?container-designator?current-container-desig)
    (spec:property?current-container-desig (:type?container-type))
    (spec:property?current-container-desig (:name?container-name))
    (spec:property?action-designator (:target?target-container-designator))
    (desig:current-designator?target-container-designator?target-container-desig)
    (spec:property?target-container-desig (:type?target-container-type))
    (spec:property?target-container-desig (:name?target-container-name))
    (-> (spec:property?action-designator (:arm?arm))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:arm?robot?arm)))
    (lisp-fun obj-int:get-object-transform?current-container-desig?container-transform)
    (lisp-fun obj-int:get-object-transform?target-container-desig?target-container-transform)
    (lisp-fun obj-int:calculate-object-faces?container-transform (?facing-robot-face?bottom-face))
    (lisp-fun obj-int:calculate-object-faces?target-container-transform (?target-facing-robot-face?target-bottom-face))
    (-> (spec:property?action-designator (:grasp?grasp))
        (true)
        (and (lisp-fun obj-int:get-object-type-grasps
                      ?container-type?facing-robot-face?bottom-face?arm
                      ?grasps)
             (member?grasp?grasps)))
    (lisp-fun obj-int:get-object-type-gripping-effort?container-type?effort)
    (lisp-fun obj-int:get-object-type-gripper-opening?container-type?gripper-opening)
    (lisp-fun obj-int:get-pouring-poses?container-name?container-type :left?grasp?container-transform?target-container-transform
             ?left-pouring-poses)
    (lisp-fun obj-int:get-pouring-poses?container-name?container-type :right?grasp?container-transform?target-container-transform
             ?right-pouring-poses)
    (lisp-fun obj-int:get-target-poses?target-container-name?target-container-type?left-pouring-poses?right-pouring-poses
              (?left-target-poses?right-target-poses)))