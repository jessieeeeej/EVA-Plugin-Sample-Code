## **
## Demo senario: 
## gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! classifier_sample ! admetadrawer ! videoconvert ! ximagesink

## This example only show how to set adlink metadata.
## So this example does not deal with any other detail concern about snchronize or other tasks.
## Only show how to retrieve the adlink metdata for user who is interested with them.
## **

# Have to install Python plugin classifier_sample.py file to the plugin folder first.
import sys
import time
import numpy
import random
from queue import Queue
# Required to import to set ADLINK inference metadata
import gst_admeta as admeta

import cv2
import gi
gi.require_version('Gst', '1.0')

from gi.repository import Gst, GObject

def extract_data(sample):
    buf = sample.get_buffer()
    caps = sample.get_caps()
    
    arr = numpy.ndarray(
        (caps.get_structure(0).get_value('height'),
         caps.get_structure(0).get_value('width'),
         3),
        buffer=buf.extract_dup(0, buf.get_size()),
        dtype=numpy.uint8)
    return arr

def new_sample(sink, data) -> Gst.FlowReturn:
    sample = sink.emit('pull-sample')
    
    # get image data and save as bmp file
    arr = extract_data(sample)
    cv2.imwrite("a.bmp", arr.copy())
    
    # get classification inference result
    buf = sample.get_buffer()
    classification_results = admeta.get_classification(buf,0)
    with classification_results as results:
        if results is not None:
            for r in results:                
                print('**********************')
                print('classification result:')
                print('id = ', r.index)
                print('output = ', r.output.decode("utf-8").strip())
                print('label = ', r.label.decode("utf-8").strip())
                print('prob = {:.3f}'.format(r.prob))
        else:
            print("None")
            
    time.sleep(0.01)
    return Gst.FlowReturn.OK

def on_message(bus: Gst.Bus, message: Gst.Message, loop: GObject.MainLoop):
    mtype = message.type
    
    if mtype == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()
    elif mtype == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("Gst.MessageType.ERROR catched in on_message:")
        print(err, debug)
        loop.quit()
    elif mtype == Gst.MessageType.ANY:
        err, debug = message.parse_warning()
        print(err, debug)

    return True

def establish_pipeline(pipeline, pipeline_elements):
    ## Add elements in pipeline.
    for element in pipeline_elements:
        pipeline.add(element)
    ## Link element one by one.
    for i in range(len(pipeline_elements) - 1):
        pipeline_elements[i].link(pipeline_elements[i + 1])


if __name__ == '__main__':
    print('Start establish pipeline.')
    # Initialize GStreamer
    Gst.init(sys.argv)

    # Create the elements
    ## element: videotesetsrc
    videosrc = Gst.ElementFactory.make("videotestsrc", "videosrc")
    
    ## element: capsfilter
    filtercaps = Gst.ElementFactory.make("capsfilter", "filtercaps")
    filtercaps.set_property("caps", Gst.Caps.from_string("video/x-raw, format=BGR, width=320, height=240"))

    ## element: classifier_sample
    classifier = Gst.ElementFactory.make("classifier_sample", "classifier")

    ## element: admetadrawer
    drawer = Gst.ElementFactory.make("admetadrawer", "drawer")

    ## element: videoconvert
    videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")

    ## element: appsink
    sink = Gst.ElementFactory.make("appsink", "sink")
    sink.set_property('emit-signals', True)
    sink.connect('new-sample', new_sample, None)
    
    # Create the empty pipeline
    pipeline = Gst.Pipeline().new("test-pipeline")
    
    # Build the pipeline
    pipeline_elements = [videosrc, filtercaps, classifier, drawer, videoconvert, sink]
    establish_pipeline(pipeline, pipeline_elements)

    # Start pipeline
    pipeline.set_state(Gst.State.PLAYING)
    loop = GObject.MainLoop()
    
    # Wait until error or EOS
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    try:
        print("Start to run the pipeline.\n")
        loop.run()
    except Exception:
        print("in exception")
        traceback.print_exc()
        loop.quit()

    # Stop Pipeline
    pipeline.set_state(Gst.State.NULL)
    del pipeline
    print('pipeline stopped.\n')