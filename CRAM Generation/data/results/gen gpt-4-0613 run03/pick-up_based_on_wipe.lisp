(<- (desig:action-grounding ?action-designator (pick-up ?resolved-action-designator))
    (spec:property ?action-designator (:type :picking))
    (spec:property ?action-designator (:grasp ?grasp))
    (spec:property ?action-designator (:arm ?arm))
    (desig:desig-prop ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-designator)
    (spec:property ?current-object-designator (:type ?object-type))
    (-> (equal ?grasp :pinch)
        (lisp-fun differentiate-object-types ?grasp ?current-object-designator ?object ?current-grasp)
        (equal ?grasp ?current-grasp))
    (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
    (-> (equal ?arm :left)
        (and (lisp-fun get-trajectory :picking ?arm ?current-grasp T ?object ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :picking
                       ?left-pick-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?left-initial-pose))
        (and (equal ?left-pick-poses NIL)
             (equal ?left-initial-pose NIL)))
    (-> (equal ?arm :right)
        (and (lisp-fun get-trajectory :picking ?arm ?current-grasp T ?object ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :picking
                       ?right-pick-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?right-initial-pose))
        (and (equal ?right-pick-poses NIL)
             (equal ?right-initial-pose NIL)))
    (desig:designator :action ((:type :picking)
                               (:collision-mode ?collision-mode)
                               (:left-pick-poses ?left-pick-poses)
                               (:right-pick-poses ?right-pick-poses)
                               (:left-initial-pose ?left-initial-pose)
                               (:right-initial-pose ?right-initial-pose))
                      ?resolved-action-designator))