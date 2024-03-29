"""
    gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! detection_sample ! admetadrawer ! videoconvert ! ximagesink
"""

import ctypes
import numpy as np
from random import random as rand, randint as rint
import time
import gst_helper
import gst_admeta as admeta

from gi.repository import Gst, GObject, GstVideo


def gst_video_caps_make(fmt):
  return  "video/x-raw, "\
    "format = (string) " + fmt + " , "\
    "width = " + GstVideo.VIDEO_SIZE_RANGE + ", "\
    "height = " + GstVideo.VIDEO_SIZE_RANGE + ", "\
    "framerate = " + GstVideo.VIDEO_FPS_RANGE


BOX_NUM = 5
DUMMY_BOXS = [[rand(), rand(), rand(), rand()] for i in range(BOX_NUM)]
def parse_inference_data_to_boxs(*data):
  # Generate dummy box here, please implement your own parse algorithm with input data
  boxs = []
  for b in DUMMY_BOXS:
    for j in range(len(b)):
      b[j] += 0.01 if rint(0, 1) == 0 else -0.01
      b[j] = max(0, b[j])
      b[j] = min(1, b[j])

    boxs.append((max(0, min(b[0], b[1])),
                 max(0, min(b[2], b[3])),
                 min(1, max(b[0], b[1])),
                 min(1, max(b[2], b[3]))))

  return boxs

class DetectionSamplePy(Gst.Element):

    # MODIFIED - Gstreamer plugin name
    GST_PLUGIN_NAME = 'detection_sample'

    __gstmetadata__ = ("Metadata addition",
                       "GstElement",
                       "Python based example for adding detection results",
                       "Lyan Hung <lyan.hung@adlinktech.com>, Dr. Paul Lin <paul.lin@adlinktech.com>")

    __gsttemplates__ = (Gst.PadTemplate.new("src",
                                            Gst.PadDirection.SRC,
                                            Gst.PadPresence.ALWAYS,
                                            Gst.Caps.from_string(gst_video_caps_make("{ BGR }"))),
                        Gst.PadTemplate.new("sink",
                                            Gst.PadDirection.SINK,
                                            Gst.PadPresence.ALWAYS,
                                            Gst.Caps.from_string(gst_video_caps_make("{ BGR }"))))

    _sinkpadtemplate = __gsttemplates__[1]
    _srcpadtemplate = __gsttemplates__[0]

    # MODIFIED - Gstreamer plugin properties
    __gproperties__ = {
    }

    def __init__(self):
      self.boxes = parse_inference_data_to_boxs()
      self.duration = 2
      self.time = time.time()
      
      super(DetectionSamplePy, self).__init__()

      self.sinkpad = Gst.Pad.new_from_template(self._sinkpadtemplate, 'sink')
      self.sinkpad.set_chain_function_full(self.chainfunc, None)
      self.sinkpad.set_chain_list_function_full(self.chainlistfunc, None)
      self.sinkpad.set_event_function_full(self.eventfunc, None)
      self.add_pad(self.sinkpad)
      self.srcpad = Gst.Pad.new_from_template(self._srcpadtemplate, 'src')
      self.add_pad(self.srcpad)


    def do_get_property(self, prop: GObject.GParamSpec):
      raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop: GObject.GParamSpec, value):
      raise AttributeError('unknown property %s' % prop.name)

    def eventfunc(self, pad: Gst.Pad, parent, event: Gst.Event) -> bool:
      return self.srcpad.push_event(event)

    def chainfunc(self, pad: Gst.Pad, parent, buff: Gst.Buffer) -> Gst.FlowReturn:
      ##################
      #     BEGINE     #
      ##################

      arr = []
      # Change random data every self.duration time
      if time.time() - self.time > self.duration:
          self.boxes = parse_inference_data_to_boxs()
          self.time = time.time()
          
      for i, box in enumerate(self.boxes):
          arr.append(admeta._DetectionBox(i, i, i, i,
                                          box[0],
                                          box[1],
                                          box[2],
                                          box[3],
                                          rand()))
      ##################
      #      END       #
      ##################

      # Set data into admetadata
      admeta.set_detection_box(buff, pad, arr)
      
      return self.srcpad.push(buff)
      
    def chainlistfunc(self, pad: Gst.Pad, parent, list: Gst.BufferList) -> Gst.FlowReturn:
      return self.srcpad.push(list.get(0))

# Register plugin to use it from command line
GObject.type_register(DetectionSamplePy)
__gstelementfactory__ = (DetectionSamplePy.GST_PLUGIN_NAME,
                         Gst.Rank.NONE, DetectionSamplePy)
