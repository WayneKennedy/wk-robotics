# References

## The design

- [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — upstream:
  STLs, BOM, print settings, links to the assembly guide. Cloned as `../SO-ARM100`.
  `Software/WEBUI_CALIBRATION.md` there describes a three-point, torque-capped calibration.
- [LeRobot SO-101 guide](https://huggingface.co/docs/lerobot/so101) — the assembly and
  commissioning tutorial this build follows: find port, set up motors, assemble, calibrate.
- [LeRobot installation](https://huggingface.co/docs/lerobot/installation) — the `feetech`
  extra is what the servo tooling needs.
- Upstream `Simulation/SO101/` — URDF and MuJoCo MJCF of the SO-101, generated with
  onshape-to-robot; the basis for any simulated two-arm work (OQ-08).
- LeRobot `robots/bi_so_follower` and `teleoperators/bi_so_leader` (in the 0.6.1 package)
  — the two-arm robot and leader definitions.

## Servos and bus

- [wk-robotics `common.md` → Actuators](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#actuators)
  — STS3215 electrical figures, adapter table, the configure-by-script procedure, power
  integrity. **The canonical family source; not restated here.**
- [Feetech software](https://www.feetechrc.com/software.html) — the FD debug GUI, for
  diagnosis only (DEC-04).
- [servodatabase: STS3215](https://servodatabase.com/servo/feetech/sts3215) — 55 ± 1 g per
  servo, the figure wk-devastator's OQ-12 uses.

## Family

- [wk-robotics](https://github.com/WayneKennedy/wk-robotics) — the index and everything
  shared.
- [koala-bot](https://github.com/WayneKennedy/koala-bot) — same servo family; vendors the
  upstream CAD as reference; its `docs/soarm-joint-pattern.md` measures the SO-101 joint
  interfaces from upstream STEP.
- [wk-devastator](https://github.com/WayneKennedy/wk-devastator) — intended mobile base;
  OQ-12 there is the tipping question.
