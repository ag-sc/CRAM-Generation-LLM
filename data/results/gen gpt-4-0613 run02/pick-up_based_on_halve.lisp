(<- (desig:action-grounding ?action-designator (pick-up ?resolved-action-designator))
    (spec:property ?action-designator (:type :picking))
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
    (-> (spec:property ?action-designator (:object-pose ?object-pose))
        (true)
        (format "Please infer where to place the object, or use the query system to infer it here"))
    (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
    (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
    (equal ?objects (?current-object-desig))
    (-> (equal ?arm :left)
        (and (lisp-fun man-int:get-action-trajectory :picking ?arm ?grasp T ?objects
                       ?left-pick-up-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?left-pick-up-pose :pick-up
                       ?left-pick-up-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?left-pick-up-pose :place-down
                       ?left-place-down-poses))
        (and (equal ?left-pick-up-poses NIL)
             (equal ?left-place-down-poses NIL)))
    (-> (equal ?arm :right)
        (and (lisp-fun man-int:get-action-trajectory :picking ?arm ?grasp T ?objects
                       ?right-pick-up-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?right-pick-up-pose :pick-up
                       ?right-pick-up-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?right-pick-up-pose :place-down
                       ?right-place-down-poses))
        (and (equal ?right-pick-up-poses NIL)
            (equal ?right-place-down-poses NIL)))
    (-> (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
        (true)
        (equal ?collision-mode nil))
    (desig:designator :action ((:type :picking)
                               (:object ?current-object-desig)
                               (:object-name  ?object-name)
                               (:arm ?arm)
                               (:gripper-opening ?gripper-opening)
                               (:effort ?effort)
                               (:grasp ?grasp)
                               (:left-pick-up-poses ?left-pick-up-poses)
                               (:right-pick-up-poses ?right-pick-up-poses)
                               (:left-place-down-poses ?left-place-down-poses)
                               (:right-place-down-poses ?right-place-down-poses)
                               (:collision-mode ?collision-mode))
                      ?resolved-action-designator))