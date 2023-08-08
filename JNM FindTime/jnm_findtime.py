"""
author: Jose N. Molina

website: jnmolina.com

description:
	Insert Key: Inserts a key at the new time.
    Buttons: Finds time between two keys or for the playback range if there is no previous/next key.

    import jnm_findtime;jnm_findtime.win()

"""
import maya.cmds as mc
import maya.mel as mm
from functools import partial
author = 'Jose N. Molina'
version = 1
website = 'jnmolina.com'
tool = 'jnm_findtime'

# from Morgan Loomis' ml_utilities http://morganloomis.com/tool/ml_utilities/
# -= ml_utilities.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Revision 34
#   / / / / / / /  2019-03-07
#  /_/ /_/ /_/_/  _________
#               /_________/
#
#     ______________
# - -/__ License __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Copyright 2018 Morgan Loomis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

MAYA_VERSION = mm.eval('getApplicationVersionAsFloat')

def createShelfButton(command, label='', name=None, description='', image=None, labelColor=(1, 0.5, 0), labelBackgroundColor=(0, 0, 0, 0.5), backgroundColor=None):
    '''
    Create a shelf button for the command on the current shelf
    '''
    # some good default icons:
    # menuIconConstraints - !
    #render_useBackground - circle
    # render_volumeShader - black dot
    #menuIconShow - eye

    gShelfTopLevel = mm.eval('$temp=$gShelfTopLevel')
    if not mc.tabLayout(gShelfTopLevel, exists=True):
        OpenMaya.MGlobal.displayWarning('Shelf not visible.')
        return

    if not name:
        name = label

    if not image:
        image = getIcon(name)
    if not image:
        image = 'render_useBackground'

    shelfTab = mc.shelfTabLayout(gShelfTopLevel, query=True, selectTab=True)
    shelfTab = gShelfTopLevel+'|'+shelfTab

    # add additional args depending on what version of maya we're in
    kwargs = {}
    if MAYA_VERSION >= 2009:
        kwargs['commandRepeatable'] = True
    if MAYA_VERSION >= 2011:
        kwargs['overlayLabelColor'] = labelColor
        kwargs['overlayLabelBackColor'] = labelBackgroundColor
        if backgroundColor:
            kwargs['enableBackground'] = bool(backgroundColor)
            kwargs['backgroundColor'] = backgroundColor

    return mc.shelfButton(parent=shelfTab, label=name, command=command, imageOverlayLabel=label, image=image, annotation=description, width=32, height=32, align='center', **kwargs)


# JNM scripts
def getTime(time):
    fourth = .25
    third = .333
    half = .5
    twothirds = .666
    threefourths = .75

    if time == 'fourth':
        return fourth
    if time == 'third':
        return third
    if time == 'half':
        return half
    if time == 'twothirds':
        return twothirds
    if time == 'threefourths':
        return threefourths


def getpbRange(*args):
    start = mc.playbackOptions(query=True, min=True)
    end = mc.playbackOptions(query=True, max=True)
    return start, end


def keyExists(t):
    if mc.keyframe(query=True, time=(t,)) == None:
        return False
    else:
        return True


def getBox(*args):
    if mc.window('jnm_findtime_win', query=True, exists=True):
        global keyInsert_box
        return mc.checkBox(keyInsert_box, query=True, value=True)


def findKeys(*args):
    pb_start, pb_end = getpbRange()
    now = mc.currentTime(query=True)
    before = mc.findKeyframe(timeSlider=True, time=(
        mc.currentTime(query=True),), which='previous')
    after = mc.findKeyframe(timeSlider=True, time=(
        mc.currentTime(query=True),), which='after')
    if keyExists(now):
        before = now
    else:
        if before > now or before == now:
            before = pb_start
    if after < now or after == now:
        after = pb_end
    return before, after, pb_start, pb_end


def goTime(time, *args):
    t = getTime(time)
    before, after, pb_start, pb_end = findKeys()
    change = (after - before) * t
    new_time = round(change + before)
    mc.currentTime(new_time)
    if getBox():
        keyInsert(new_time)
    return new_time


def keyInsert(new_time):
    sel = mc.ls(sl=1)
    mc.refresh(suspend=True)
    for i in sel:
        mc.setKeyframe(time=(new_time, new_time), insert=True)
        mc.currentTime(new_time)
    mc.refresh(suspend=False)


def about(*args):
    text = 'Author: ' + author + '\n\n' + 'Version: ' + \
        str(version) + '\n\n' + 'Website: ' + website
    mc.confirmDialog(title='About', message=text, button='Close')

# use ml_utilities.createShelfButton for popup button to create shelf button for the tool
def popUpShelfBtn(parent, shelf_label, shelf_desc, cmds, image=tool):
    mc.popupMenu(parent=parent)
    cmd = "import " + tool + ";" + tool + "." + str(cmds)
    command = "import {tool};{tool}.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(tool=tool,
        cmd=cmd, shelf_label=shelf_label, shelf_desc=shelf_desc, image=image)
    mc.menuItem(label="Create Shelf Button",
                command=command, enableCommandRepeat=True)


fourth_anno = 'Find time 1/4 between two keys.'
third_anno = 'Find time 1/3 between two keys.'
half_anno = 'Find time 1/2 between two keys.'
twothirds_anno = 'Find time 2/3 between two keys.'
threefourths_anno = 'Find time 3/4 between two keys.'
keyInsert_box_anno = 'Insert key at new time.'

w = 315

def win(*args):
    if mc.window('jnm_findtime_win', q=True, ex=True):
        mc.deleteUI('jnm_findtime_win')

    mc.window('jnm_findtime_win', title='JNM Find Time',
              resizeToFitChildren=True, height=50, width=w, menuBar=True)
    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Website', command=(
        'import maya.cmds as mc;mc.showHelp("http://www.'+website+'",absolute=True)'))
    mc.columnLayout(adj=True)
    mc.rowColumnLayout(numberOfColumns=1)
    global keyInsert_box
    keyInsert_box = mc.checkBox(
        label='Insert Key', annotation=keyInsert_box_anno)
    mc.setParent('..')
    mc.separator(style='single', horizontal=True, h=10)
    mc.rowColumnLayout(numberOfRows=1)
    fourth_btn = mc.button(
        label='1/4', command=partial(goTime, 'fourth'), annotation=fourth_anno, w=w/5)
    popUpShelfBtn(fourth_btn, '1/4', fourth_anno, 'goTime(\'fourth\')')
    third_btn = mc.button(
        label='1/3', command=partial(goTime, 'third'), annotation=third_anno, w=w/5)
    popUpShelfBtn(third_btn, '1/3', third_anno, 'goTime(\'third\')')
    half_btn = mc.button(
        label='1/2', command=partial(goTime, 'half'), annotation=half_anno, w=w/5)
    popUpShelfBtn(half_btn, '1/2', half_anno, 'goTime(\'half\')')
    twothirds_btn = mc.button(
        label='2/3', command=partial(goTime, 'twothirds'), annotation=twothirds_anno, w=w/5)
    popUpShelfBtn(twothirds_btn, '2/', twothirds_anno,
                  'goTime(\'twothirds\')')
    threefourths_btn = mc.button(
        label='3/4', command=partial(goTime, 'threefourths'), annotation=threefourths_anno, w=w/5)
    popUpShelfBtn(threefourths_btn, '3/4', threefourths_anno,
                  'goTime(\'threefourths\')')
    mc.setParent('..')
    mc.columnLayout(adj=True)
    mc.helpLine()
    mc.showWindow()
