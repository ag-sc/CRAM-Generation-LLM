(<- (desig:action-grounding ?action-designator (place-down ?resolved-action-designator))
    (spec:property ?action-designator (:type :placing))
    (spec:property ?action-designator (:grasp ?grasp))
    (spec:property ?action-designator (:arm ?arm))
    (desig:desig-prop ?action-designator (:location ?location-designator))
    (desig:current-designator ?location-designator ?current-location-designator)
    (spec:property ?current-location-designator (:type ?location-type))
    (equal ?location (?current-location-designator))
    (-> (equal ?grasp :holding)
        (lisp-fun differentiate-location-types ?grasp ?location ?current-grasp)
        (equal ?grasp ?current-grasp))
    (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
    (-> (equal ?arm :left)
        (and (lisp-fun get-trajectory :placing ?arm ?current-grasp T ?location ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :placing
                       ?left-place-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?left-initial-pose))
        (and (equal ?left-place-poses NIL)
             (equal ?left-initial-pose NIL)))
    (-> (equal ?arm :right)
        (and (lisp-fun get-trajectory :placing ?arm ?current-grasp T ?location ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :placing
                       ?right-place-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?right-initial-pose))
        (and (equal ?right-place-poses NIL)
             (equal ?right-initial-pose NIL)))
    (desig:designator :action ((:type :placing)
                               (:collision-mode ?collision-mode)
                               (:left-place-poses ?left-place-poses)
                               (:right-place-poses ?right-place-poses)
                               (:left-initial-pose ?left-initial-pose)
                               (:right-initial-pose ?right-initial-pose))
                      ?resolved-action-designator))