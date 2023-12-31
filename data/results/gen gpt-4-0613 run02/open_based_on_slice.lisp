(<- (desig:action-grounding ?action-designator (open ?resolved-action-designator))
    (spec:property ?action-designator (:type :opening))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (man-int:robot-free-hand ?_ ?arm))
    (lisp-fun man-int:get-object-old-transform ?current-object-desig ?object-transform)
    (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun man-int:get-action-grasps ?object-type ?arm ?object-transform ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
    (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
    (equal ?objects (?current-object-desig))
    (-> (equal ?arm :left)
        (and (lisp-fun man-int:get-action-trajectory :opening ?arm ?grasp T ?objects
                       ?left-opening-pose))
        (equal ?left-opening-pose NIL))
    (-> (equal ?arm :right)
        (and (lisp-fun man-int:get-action-trajectory :opening ?arm ?grasp T ?objects
                       ?right-opening-pose))
        (equal ?right-opening-pose NIL))
    (-> (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
        (true)
        (equal ?collision-mode nil))
    (desig:designator :action ((:type :opening)
                               (:object ?current-object-desig)
                               (:object-name  ?object-name)
                               (:arm ?arm)
                               (:gripper-opening ?gripper-opening)
                               (:effort ?effort)
                               (:grasp ?grasp)
                               (:left-opening-pose ?left-opening-pose)
                               (:right-opening-pose ?right-opening-pose)
                               (:collision-mode ?collision-mode))
                      ?resolved-action-designator))