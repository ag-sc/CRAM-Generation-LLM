(<- (desig:action-grounding ?action-designator (pick-up ?resolved-action-designator))
    (spec:property ?action-designator (:type :picking-up))
    (spec:property ?action-designator (:grasp ?grasp))
    (spec:property ?action-designator (:arm ?arm))
    (desig:desig-prop ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-designator)
    (spec:property ?current-object-designator (:type ?object-type))
    (equal ?object (?current-object-designator))
    (-> (equal ?grasp :pinching)
        (lisp-fun differentiate-object-types ?grasp ?object ?current-grasp)
        (equal ?grasp ?current-grasp))
    (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
    (-> (equal ?arm :left)
        (and (lisp-fun get-trajectory :picking-up ?arm ?current-grasp T ?object ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :picking-up
                       ?left-pick-up-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?left-initial-pose))
        (and (equal ?left-pick-up-poses NIL)
             (equal ?left-initial-pose NIL)))
    (-> (equal ?arm :right)
        (and (lisp-fun get-trajectory :picking-up ?arm ?current-grasp T ?object ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :picking-up
                       ?right-pick-up-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?right-initial-pose))
        (and (equal ?right-pick-up-poses NIL)
             (equal ?right-initial-pose NIL)))
    (desig:designator :action ((:type :picking-up)
                               (:collision-mode ?collision-mode)
                               (:left-pick-up-poses ?left-pick-up-poses)
                               (:right-pick-up-poses ?right-pick-up-poses)
                               (:left-initial-pose ?left-initial-pose)
                               (:right-initial-pose ?right-initial-pose))
                      ?resolved-action-designator))