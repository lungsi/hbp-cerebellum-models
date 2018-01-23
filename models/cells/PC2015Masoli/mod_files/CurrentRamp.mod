COMMENT
CurrentRamp.mod
This is a custim mod file that creates an overall ramp for different current amplitudes; not just steps of different amplitudes. For Purkinje Cell PC2015Masoli this is specifically used for running the quasilinear test. As per Stefano Masoli's experience the quasilinear behavior seen in biological Purkinje cells is reproducible in PC2015Masoli model when injection of varying amplitudes is given as ramps (not as steps).

A generic ramp can be created by taking the difference of two unit steps such that one is shifted differently. The mathematical form in this mod is as follows:
- ramp starts at t1 => u(t - t1), first unit step turned on at t1
- ramp ends at t2 =>   u(t - t2), second unit step turned on at t2
- unit step only between t1 & t2 => u(t-t1) - u(t-t2)
- ramp starting from t1 and ending at t2 with
     amplitude=1 at the end of the ramp
     => (u(t-t1) - u(t-t2)) * ((t-t1)/(t2-t1))
- the same ramp with desired starting and ending amplitudes is given by
  (u(t-t1) - u(t-t2)) * ((t-t1)/(t2-t1)) * amp_final + amp_initial

The default IClamp is done as stim_current_clamp = h.IClamp(0.5, sec=soma).
Similarly,
stim_current_ramp = h.IRamp(0.5, sec=soma)

Parameters of IClamp are set as
stim_current_clamp.delay, stim_current_clamp.dur, stim_current_clamp.amp

But parameters of IRamp they are set as
stim_current_ramp.delay, stim_current_ramp.dur,
stim_current_ramp.amp_initial, stim_rurrent_ramp.amp_final

NOTE: t1 -> delay and (t2-t1) -> dur
ENDCOMMENT

NEURON {
        POINT_PROCESS IRamp
        RANGE delay, dur, amp_initial, amp_final, unit_step_t1, unit_step_t2, i
        ELECTRODE_CURRENT i
}

UNITS {
        (nA) = (nanoamp)
}

PARAMETER {
        delay (ms)
        dur (ms)   <0, 1e9>
        amp_initial (nA)
        amp_final (nA)
}

ASSIGNED {
        unit_step_t1
        unit_step_t2
        i (nA)
}

INITIAL {
        unit_step_t1 = 0
        unit_step_t2 = 0
        i = 0
}

BREAKPOINT {
        at_time(delay)
        at_time(delay+dur)

        if (t >= delay) {
           unit_step_t1 = 1
        }else{
           unit_step_t1 = 0
        }

        if (t >= delay+dur) {
           unit_step_t2 = 1
        }else{
           unit_step_t2 = 0
        }

        if (t >= delay && t <= delay+dur) {
           i = (unit_step_t1 - unit_step_t2)*((t-delay)/dur)*amp_final + amp_initial
        }else{
           i = 0
        }
}
