(<- (desig:action-grounding ?action-designator (pp-plans:place-down ?resolved-action-designator))
      (spec:property ?action-designator (:type :placing))
      (spec:property ?action-designator (:object ?object-designator))
      (desig:current-designator ?object-designator ?current-object-desig)
      (spec:property ?current-object-desig (:type ?object-type))
      (spec:property ?current-object-desig (:name ?object-name))
      (spec:property ?action-designator (:location ?location-designator))
      (desig:current-designator ?location-designator ?current-location-desig)
      (spec:property ?current-location-desig (:type ?location-type))
      (spec:property ?current-location-desig (:name ?location-name))
      (-> (spec:property ?action-designator (:arm ?arm))
          (true)
          (man-int:robot-free-hand ?_ ?arm))
      (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
      (lisp-fun man-int:get-location-transform ?current-location-desig ?location-transform)
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
          (and (lisp-fun man-int:get-action-trajectory :placing-down ?arm ?grasp T ?objects
                         ?left-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :reaching
                         ?left-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :grasping
                         ?left-grasp-poses))
          (and (equal ?left-reach-poses NIL)
               (equal ?left-grasp-poses NIL)))
      (-> (equal ?arm :right)
          (and (lisp-fun man-int:get-action-trajectory :placing-down ?arm ?grasp T ?objects
                         ?right-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :reaching
                         ?right-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :grasping
                         ?right-grasp-poses))
          (and (equal ?right-reach-poses NIL)
               (equal ?right-grasp-poses NIL)))
      (desig:designator :action ((:type :placing-down)
                                 (:object ?current-object-desig)
                                 (:object-name  ?object-name)
                                 (:location ?current-location-desig)
                                 (:location-name ?location-name)
                                 (:arm ?arm)
                                 (:gripper-opening ?gripper-opening)
                                 (:effort ?effort)
                                 (:grasp ?grasp)
                                 (:left-reach-poses ?left-reach-poses)
                                 (:right-reach-poses ?right-reach-poses)
                                 (:left-grasp-poses ?left-grasp-poses)
                                 (:right-grasp-poses ?right-grasp-poses)
                                 (:place :placing))
                        ?resolved-action-designator)))