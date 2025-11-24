(<- (desig:action-grounding?action-designator (slice?resolved-action-designator))
    (spec:property?action-designator (:type :slicing))
    (spec:property?action-designator (:grasp?grasp))
    (spec:property?action-designator (:arm?arm))
    (desig:desig-prop?action-designator (:object?object-designator))
    (desig:current-designator?object-designator?current-object-designator)
    (spec:property?current-object-designator (:type?object-type))
    (equal?object (?current-object-designator))
    (-> (equal?grasp :cutting)
        (lisp-fun differentiate-object-types?grasp?object?current-grasp)
        (equal?grasp?current-grasp))
    (desig:desig-prop?action-designator (:cutting-mode?cutting-mode))
    (-> (equal?arm :left)
        (and (lisp-fun get-trajectory :slicing?arm?current-grasp T?object?lists)
             (lisp-fun man-int:get-traj-poses-by-label?lists :slicing
                      ?left-slice-poses)
             (lisp-fun man-int:get-traj-poses-by-label?lists :initial
                      ?left-initial-pose)
             (lisp-fun man-int:get-traj-poses-by-label?lists :final
                      ?left-final-pose))
        (and (equal?left-slice-poses (list?small-slice-pose?big-slice-pose))
             (equal?left-initial-pose?start-pose)
             (equal?left-final-pose?end-pose)))
    (-> (equal?arm :right)
        (and (lisp-fun get-trajectory :slicing?arm?current-grasp T?object?lists)
             (lisp-fun man-int:get-traj-poses-by-label?lists :slicing
                      ?right-slice-poses)
             (lisp-fun man-int:get-traj-poses-by-label?lists :initial
                      ?right-initial-pose)
             (lisp-fun man-int:get-traj-poses-by-label?lists :final
                      ?right-final-pose))
        (and (equal?right-slice-poses (list?small-slice