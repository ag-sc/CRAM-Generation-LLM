(<- (desig:action-grounding ?action-designator (halve ?resolved-action-designator))
    (spec:property ?action-designator (:type :halving))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (man-int:robot-free-hand ?_ ?arm))
    (lisp-fun man-int:get-object-old-transform ?current-object-desig ?object-transform)
    (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (man-int:object-rotationally-symmetric ?object-type)
        (equal ?rotationally-symmetric t)
        (equal ?rotationally-symmetric nil))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun man-int:get-action-grasps ?object-type ?arm ?object-transform ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
    (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
    (equal ?objects (?current-object-desig))
    (-> (equal ?arm :left)
        (and (lisp-fun man-int:get-action-trajectory :halving ?arm ?grasp T ?objects
                       ?left-halving-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?left-halving-pose :halve-up
                       ?left-halve-up-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?left-halving-pose :halve-down
                       ?left-halve-down-poses))
        (and (equal ?left-halve-up-poses NIL)
             (equal ?left-halve-down-poses NIL)))
    (-> (equal ?arm :right)
        (and (lisp-fun man-int:get-action-trajectory :halving ?arm ?grasp T ?objects
                       ?right-halving-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?right-halving-pose :halve-up
                       ?right-halve-up-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?right-halving-pose :halve-down
                       ?right-halve-down-poses))
        (and(equal ?right-halve-up-poses NIL)
            (equal ?right-halve-down-poses NIL)))
    (-> (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
        (true)
        (equal ?collision-mode nil))
    (desig:designator :action ((:type :halving)
                               (:object ?current-object-desig)
                               (:object-name  ?object-name)
                               (:arm ?arm)
                               (:gripper-opening ?gripper-opening)
                               (:effort ?effort)
                               (:grasp ?grasp)
                               (:left-halve-up-poses ?left-halve-up-poses)
                               (:right-halve-up-poses ?right-halve-up-poses)
                               (:left-halve-down-poses ?left-halve-down-poses)
                               (:right-halve-down-poses ?right-halve-down-poses)
                               (:collision-mode ?collision-mode))
                      ?resolved-action-designator))