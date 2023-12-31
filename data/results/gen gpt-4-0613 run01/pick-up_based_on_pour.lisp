(<- (desig:action-grounding ?action-designator (pick-up ?resolved-action-designator))
    (spec:property ?action-designator (:type :picking-up))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
     (-> (spec:property ?action-designator (:arms ?arms))
        (true)
        (and (man-int:robot-free-hand ?_ ?arm)
             (equal ?arms (?arm))))
     (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (man-int:object-rotationally-symmetric ?object-type)
        (equal ?rotationally-symmetric t)
        (equal ?rotationally-symmetric nil))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (member ?arm ?arms)
             (lisp-fun man-int:get-action-grasps ?object-type ?arm ?object-transform ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
    (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
    (equal ?objects (?current-object-desig))
    (-> (member :left ?arms)
        (and (lisp-fun man-int:get-action-trajectory :picking-up :left ?grasp T ?objects
                       ?left-pick-up-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?left-pick-up-pose :approach
                       ?left-approach-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?left-pick-up-pose :lifting
                       ?left-lift-poses))
        (and (equal ?left-approach-poses NIL)
             (equal ?left-lift-poses NIL)))
     (-> (member :right ?arms)
        (and (lisp-fun man-int:get-action-trajectory :picking-up :right ?grasp T ?objects
                       ?right-pick-up-pose)
             (lisp-fun man-int:get-traj-poses-by-label ?right-pick-up-pose :approach
                       ?right-approach-poses)
             (lisp-fun man-int:get-traj-poses-by-label ?right-pick-up-pose :lifting
                       ?right-lift-poses))
        (and (equal ?right-approach-poses NIL)
             (equal ?right-lift-poses NIL)))
     (-> (desig:desig-prop ?action-designator (:collision-mode ?collision-mode))
        (true)
        (equal ?collision-mode nil))
    (desig:designator :action ((:type :picking-up)
                               (:object ?current-object-desig)
                               (:object-type ?object-type)
                               (:object-name  ?object-name)
                               (:arms ?arms)
                               (:grasp ?grasp)
                               (:left-approach-poses ?left-approach-poses)
                               (:right-approach-poses ?right-approach-poses)
                               (:left-lift-poses ?left-lift-poses)
                               (:right-lift-poses ?right-lift-poses)
                               (:collision-mode ?collision-mode))
                      ?resolved-action-designator))