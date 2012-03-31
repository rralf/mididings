# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

from mididings.units.base import _Unit, Filter, Split, Pass
from mididings.units.splits import VelocitySplit
from mididings.units.generators import NoteOn, NoteOff

import mididings.util as _util
import mididings.misc as _misc
import mididings.overload as _overload
import mididings.constants as _constants
import mididings.arguments as _arguments
import mididings.unitrepr as _unitrepr


@_unitrepr.accept(_util.port_number)
def Port(port):
    """
    Change port number.
    """
    return _Unit(_mididings.Port(_util.actual(port)))


@_unitrepr.accept(_util.channel_number)
def Channel(channel):
    """
    Change channel number.a
    """
    return _Unit(_mididings.Channel(_util.actual(channel)))


@_unitrepr.accept(int)
def Transpose(offset):
    """
    Transpose note events.
    """
    return _Unit(_mididings.Transpose(offset))


@_arguments.accept(_util.note_number)
def Key(note):
    """
    Change note number.
    """
    return Filter(_constants.NOTE) % Split({
        _constants.NOTEON:  NoteOn(note, _constants.EVENT_VELOCITY),
        _constants.NOTEOFF: NoteOff(note, _constants.EVENT_VELOCITY),
    })


@_overload.mark(
    """
    Change note-on velocity.
    """
)
@_unitrepr.accept(int)
def Velocity(offset):
    return _Unit(_mididings.Velocity(offset, 1))

@_overload.mark
@_unitrepr.accept((float, int))
def Velocity(multiply):
    return _Unit(_mididings.Velocity(multiply, 2))

@_overload.mark
@_unitrepr.accept(_util.velocity_value)
def Velocity(fixed):
    return _Unit(_mididings.Velocity(fixed, 3))

@_overload.mark
@_unitrepr.accept((float, int))
def Velocity(gamma):
    return _Unit(_mididings.Velocity(gamma, 4))

@_overload.mark
@_unitrepr.accept((float, int))
def Velocity(curve):
    return _Unit(_mididings.Velocity(curve, 5))

@_overload.mark
@_unitrepr.accept((float, int), int)
def Velocity(multiply, offset):
    return Velocity(multiply=multiply) >> Velocity(offset=offset)


@_overload.mark(
    """
    Apply a linear slope to note-on velocities.
    """
)
@_unitrepr.accept(_arguments.sequenceof(_util.note_limit), _arguments.sequenceof(int))
def VelocitySlope(notes, offset):
    _check_velocity_slope(notes, offset)
    return _Unit(_mididings.VelocitySlope(notes, offset, 1))

@_overload.mark
@_unitrepr.accept(_arguments.sequenceof(_util.note_limit), _arguments.sequenceof((float, int)))
def VelocitySlope(notes, multiply):
    _check_velocity_slope(notes, multiply)
    return _Unit(_mididings.VelocitySlope(notes, multiply, 2))

@_overload.mark
@_unitrepr.accept(_arguments.sequenceof(_util.note_limit), _arguments.sequenceof(_util.velocity_value))
def VelocitySlope(notes, fixed):
    _check_velocity_slope(notes, fixed)
    return _Unit(_mididings.VelocitySlope(notes, fixed, 3))

@_overload.mark
@_unitrepr.accept(_arguments.sequenceof(_util.note_limit), _arguments.sequenceof((float, int)))
def VelocitySlope(notes, gamma):
    _check_velocity_slope(notes, gamma)
    return _Unit(_mididings.VelocitySlope(notes, gamma, 4))

@_overload.mark
@_unitrepr.accept(_arguments.sequenceof(_util.note_limit), _arguments.sequenceof((float, int)))
def VelocitySlope(notes, curve):
    _check_velocity_slope(notes, curve)
    return _Unit(_mididings.VelocitySlope(notes, curve, 5))

@_overload.mark
@_unitrepr.accept(_arguments.sequenceof(_util.note_limit), _arguments.sequenceof((float, int)), _arguments.sequenceof(int))
def VelocitySlope(notes, multiply, offset):
    return VelocitySlope(notes, multiply=multiply) >> VelocitySlope(notes, offset=offset)


def _check_velocity_slope(notes, params):
    if len(notes) != len(params):
        raise ValueError("invalid parameters to VelocitySlope(): notes and velocity values must be sequences of the same length")
    if len(notes) < 2:
        raise ValueError("invalid parameters to VelocitySlope(): need at least two notes")
    if sorted(notes) != notes:
        raise ValueError("invalid parameters to VelocitySlope(): notes must be in ascending order")


@_overload.mark(
    """
    Limit velocities to a given range.
    """
)
@_arguments.accept(_util.velocity_limit, _util.velocity_limit)
def VelocityLimit(min, max):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, min):   Velocity(fixed=min),
        (min, max): Pass(),
        (max, 0):   Velocity(fixed=max),
    })

@_overload.mark
@_arguments.accept(_util.velocity_limit)
def VelocityLimit(max):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, max):   Pass(),
        (max, 0):   Velocity(fixed=max),
    })

@_overload.mark
@_arguments.accept(_util.velocity_limit)
def VelocityLimit(min):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, min):   Velocity(fixed=min),
        (min, 0):   Pass(),
    })


@_unitrepr.accept(_util.ctrl_number, _util.ctrl_number)
def CtrlMap(ctrl_in, ctrl_out):
    """
    Convert one controller to another.
    """
    return _Unit(_mididings.CtrlMap(ctrl_in, ctrl_out))


@_unitrepr.accept(_util.ctrl_number, int, int, int, int)
def CtrlRange(ctrl, min, max, in_min=0, in_max=127):
    """
    Convert controller range.
    """
    if in_min > in_max:
        # swap ranges so that in_min is less than in_max
        in_min, in_max = in_max, in_min
        min, max = max, min
    return _Unit(_mididings.CtrlRange(ctrl, min, max, in_min, in_max))


@_overload.mark(
    """
    Transform controller values.
    """
)
@_unitrepr.accept(_util.ctrl_number, (float, int))
def CtrlCurve(ctrl, gamma):
    return _Unit(_mididings.CtrlCurve(ctrl, gamma, 4))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, (float, int))
def CtrlCurve(ctrl, curve):
    return _Unit(_mididings.CtrlCurve(ctrl, curve, 5))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, int)
def CtrlCurve(ctrl, offset):
    return _Unit(_mididings.CtrlCurve(ctrl, offset, 1))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, (float, int))
def CtrlCurve(ctrl, multiply):
    return _Unit(_mididings.CtrlCurve(ctrl, multiply, 2))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, (float, int), int)
def CtrlCurve(ctrl, multiply, offset):
    return CtrlCurve(ctrl, multiply=multiply) >> CtrlCurve(ctrl, offset=offset)



@_overload.mark(
    """
    Modify pitchbend range.
    """
)
@_unitrepr.accept(int, int, int, int)
def PitchbendRange(min, max, in_min=-8192, in_max=8191):
    return _Unit(_mididings.PitchbendRange(min, max, in_min, in_max))

@_overload.mark
@_unitrepr.accept(int, int, int)
def PitchbendRange(down, up, range):
    return PitchbendRange(int(float(down)/range*8192), int(float(up)/range*8191))
