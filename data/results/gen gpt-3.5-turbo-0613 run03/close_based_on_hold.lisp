(<- (desig:action-grounding ?action-designator (pp-plans:close-container ?resolved-action-designator))
      (spec:property ?action-designator (:type :closing))
      (spec:property ?action-designator (:object ?object-designator))
      (desig:current-designator ?object-designator ?current-object-desig)
      (spec:property ?current-object-desig (:type ?object-type))
      (spec:property ?current-object-desig (:name ?object-name))
      (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
      (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
      (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
      (lisp-fun man-int:get-action-gripper-opening ?object-type ?gripper-opening)
      (equal ?objects (?current-object-desig))
      (-> (equal ?arm :left)
          (and (lisp-fun man-int:get-action-trajectory :closing ?arm T ?objects
                         ?left-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :reaching
                         ?left-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :grasping
                         ?left-grasp-poses))
          (and (equal ?left-reach-poses NIL)
               (equal ?left-grasp-poses NIL)))
      (-> (equal ?arm :right)
          (and (lisp-fun man-int:get-action-trajectory :closing ?arm T ?objects
                         ?right-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :reaching
                         ?right-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :grasping
                         ?right-grasp-poses))
          (and (equal ?right-reach-poses NIL)
               (equal ?right-grasp-poses NIL)))
      (desig:designator :action ((:type :closing)
                                 (:object ?current-object-desig)
                                 (:object-name  ?object-name)
                                 (:arm ?arm)
                                 (:gripper-opening ?gripper-opening)
                                 (:effort ?effort)
                                 (:left-reach-poses ?left-reach-poses)
                                 (:right-reach-poses ?right-reach-poses)
                                 (:left-grasp-poses ?left-grasp-poses)
                                 (:right-grasp-poses ?right-grasp-poses)
                                 (:close-container :closing))
                        ?resolved-action-designator)))