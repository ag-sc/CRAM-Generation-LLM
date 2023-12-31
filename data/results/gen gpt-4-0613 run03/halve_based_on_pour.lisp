(<- (desig:action-grounding ?action-designator (halve ?resolved-action-designator))
    (spec:property ?action-designator (:type :cutting))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (spec:property ?action-designator (:arms ?arms))
        (true)
        (and (man-int:robot-free-hand ?_ ?arm)
             (equal ?arms (?arm))))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (member ?arm ?arms)
             (lisp-fun man-int:get-action-grasps ?object-type ?arm ?object-transform ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
    (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
    (equal ?objects (?current-object-desig))
    (-> (member :left ?arms)
        (and (lisp-fun man-int:get-action-trajectory :cutting :left ?grasp T ?objects
                       ?left-cutting-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?left-cutting-pose :approach
                       ?left-approach-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?left-cutting-pose :cutting
                       ?left-cutting-poses))
        (and (equal ?left-approach-poses NIL)
             (equal ?left-cutting-poses NIL)))
     (-> (member :right ?arms)
        (and (lisp-fun man-int:get-action-trajectory :cutting :right ?grasp T ?objects
                       ?right-cutting-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?right-cutting-pose :approach
                       ?right-approach-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?right-cutting-pose :cutting
                       ?right-cutting-poses))
        (and (equal ?right-approach-poses NIL)
             (equal ?right-cutting-poses NIL)))
     (-> (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
        (true)
        (equal ?collision-mode nil))
    (desig:designator :action ((:type :cutting)
                               (:object ?current-object-desig)
                               (:object-type ?object-type)
                               (:object-name  ?object-name)
                               (:arms ?arms)
                               (:grasp ?grasp)
                               (:left-approach-poses ?left-approach-poses)
                               (:right-approach-poses ?right-approach-poses)
                               (:left-cutting-poses ?left-cutting-poses)
                               (:right-cutting-poses ?right-cutting-poses)
                               (:collision-mode ?collision-mode))
                      ?resolved-action-designator))