(<- (desig:action-grounding ?action-designator (hold ?resolved-action-designator))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (man-int:robot-free-hand ?_ ?arm))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun man-int:get-action-grasps ?object-type ?arm ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
    (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
    (equal ?objects (?current-object-desig))
    (-> (equal ?arm :left)
        (and (lisp-fun man-int:get-action-trajectory :holding ?arm ?grasp T ?objects
                       ?left-holding-pose))
        (equal ?left-holding-pose NIL))
    (-> (equal ?arm :right)
        (and (lisp-fun man-int:get-action-trajectory :holding ?arm ?grasp T ?objects
                       ?right-holding-pose))
        (equal ?right-holding-pose NIL))
    (-> (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
        (true)
        (equal ?collision-mode nil))
    (desig:designator :action ((:type :holding)
                               (:object ?current-object-desig)
                               (:object-name  ?object-name)
                               (:arm ?arm)
                               (:gripper-opening ?gripper-opening)
                               (:effort ?effort)
                               (:grasp ?grasp)
                               (:left-holding-pose ?left-holding-pose)
                               (:right-holding-pose ?right-holding-pose)
                               (:collision-mode ?collision-mode))
                      ?resolved-action-designator))