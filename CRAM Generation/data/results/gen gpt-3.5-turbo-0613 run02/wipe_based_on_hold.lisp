(<- (desig:action-grounding ?action-designator (pp-plans:wipe ?resolved-action-designator))
      (spec:property ?action-designator (:type :cleaning))
      (spec:property ?action-designator (:object ?object-designator))
      (desig:current-designator ?object-designator ?current-object-desig)
      (spec:property ?current-object-desig (:type ?object-type))
      (spec:property ?current-object-desig (:name ?object-name))
      (-> (spec:property ?action-designator (:tool ?tool-designator))
          (desig:current-designator ?tool-designator ?current-tool-desig)
          (spec:property ?current-tool-desig (:type ?tool-type))
          (spec:property ?current-tool-desig (:name ?tool-name)))
      (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
      (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
      (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun man-int:get-action-grasps ?object-type ?grasp ?object-transform ?grasps)
           (member ?grasp ?grasps)))
      (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
      (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
      (equal ?objects (?current-object-desig ?current-tool-desig))
      (-> (equal ?arm :left)
          (and (lisp-fun man-int:get-action-trajectory :wiping ?arm ?grasp T ?objects
                         ?left-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :reaching
                         ?left-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :grasping
                         ?left-grasp-poses))
          (and (equal ?left-reach-poses NIL)
               (equal ?left-grasp-poses NIL)))
      (-> (equal ?arm :right)
          (and (lisp-fun man-int:get-action-trajectory :wiping ?arm ?grasp T ?objects
                         ?right-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :reaching
                         ?right-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :grasping
                         ?right-grasp-poses))
          (and (equal ?right-reach-poses NIL)
               (equal ?right-grasp-poses NIL)))
      (desig:designator :action ((:type :wiping)
                                 (:object ?current-object-desig)
                                 (:object-name  ?object-name)
                                 (:tool ?current-tool-desig)
                                 (:tool-name ?tool-name)
                                 (:arm ?arm)
                                 (:gripper-opening ?gripper-opening)
                                 (:effort ?effort)
                                 (:grasp ?grasp)
                                 (:left-reach-poses ?left-reach-poses)
                                 (:right-reach-poses ?right-reach-poses)
                                 (:left-grasp-poses ?left-grasp-poses)
                                 (:right-grasp-poses ?right-grasp-poses)
                                 (:clean :cleaning))
                        ?resolved-action-designator))