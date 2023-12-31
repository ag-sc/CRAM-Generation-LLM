(<- (desig:action-grounding ?action-designator (open ?resolved-action-designator))
    (spec:property ?action-designator (:type :opening))
    (spec:property ?action-designator (:grasp ?grasp))
    (spec:property ?action-designator (:arm ?arm))
    (desig:desig-prop ?action-designator (:container ?container-designator))
    (desig:current-designator ?container-designator ?current-container-designator)
    (spec:property ?current-container-designator (:type ?container-type))
    (equal ?container (?current-container-designator))
    (-> (equal ?grasp :opening)
        (lisp-fun differentiate-container-types ?grasp ?container ?current-grasp)
        (equal ?grasp ?current-grasp))
    (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
    (-> (equal ?arm :left)
        (and (lisp-fun get-trajectory :opening ?arm ?current-grasp T ?container ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :opening
                       ?left-open-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?left-initial-pose))
        (and (equal ?left-open-poses NIL)
             (equal ?left-initial-pose NIL)))
    (-> (equal ?arm :right)
        (and (lisp-fun get-trajectory :opening ?arm ?current-grasp T ?container ?lists)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :opening
                       ?right-open-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?lists :initial
                       ?right-initial-pose))
        (and (equal ?right-open-poses NIL)
             (equal ?right-initial-pose NIL)))
    (desig:designator :action ((:type :opening)
                               (:collision-mode ?collision-mode)
                               (:left-open-poses ?left-open-poses)
                               (:right-open-poses ?right-open-poses)
                               (:left-initial-pose ?left-initial-pose)
                               (:right-initial-pose ?right-initial-pose))
                      ?resolved-action-designator))