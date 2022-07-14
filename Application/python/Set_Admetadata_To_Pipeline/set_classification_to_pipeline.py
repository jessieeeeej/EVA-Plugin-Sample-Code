## **
## Demo senario: 
## gst-launch-1.0 videotestsrc ! video/x-raw, format=BGR, width=320, height=240, framerate=30/1 ! videoconvert ! admetadebuger type=0 id=187 class=boy prob=0.876 ! appsink

## This example only show how to set adlink metadata from appsrc.
## So this example does not deal with any other detail concern about snchronize or other tasks.
## Only show how to retrieve the adlink metdata for user who is interested with them.
## **
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

grabVec = Queue()

def need_data(src, length) -> Gst.FlowReturn:
    # wait for image data vector, grabVec, is not full
    while True:
        time.sleep(0.001)
        if grabVec.qsize() > 0:
            break
    
    global num_frames
    if grabVec.qsize() > 0:
        # get image data from vector
        buf = Gst.Buffer.new_allocate(None, length, None)
        buf.fill(0, grabVec.get().tostring())
        
        # set buffer timestamp
        buf.duration = 1/ 30 * Gst.SECOND
        buf.pts = buf.dts = int(num_frames * buf.duration)
        buf.offset = num_frames * buf.duration
        num_frames += 1
        
        # push buffer to appsrc
        retval = src.emit('push-buffer', buf)
        if retval != Gst.FlowReturn.OK:
            print("retval = ", retval)
            
        time.sleep(0.01)

def enough_data(src, size, length) -> Gst.FlowReturn:
    return Gst.FlowReturn.OK

def push_buffer(src) -> Gst.FlowReturn:
    buf = Gst.Buffer.new()
    labels = ['water bottle', 'camera', 'chair', 'person', 'slipper', 'mouse', 'Triceratops', 'woodpecker']
    duration = 2
    time_1 = time.time()

    cls = []
    # Change random data every self.duration time
    if time.time() - time_1 > duration:
        class_id = random.randrange(len(labels))
        class_prob = random.uniform(0, 1)
        time_1 = time.time()
      
    cls.append(admeta._Classification(class_id, '', labels[class_id], class_prob))
    # push buffer to appsrc
    admeta.set_classification(buf, src, cls)
    classification = src.emit('push-buffer', buf)
    with classification as results:
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
            
    time.sleep(1)
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
    videosrc.connect('push-buffer', push_buffer)
    
    ## element: capsfilter
    filtercaps = Gst.ElementFactory.make("capsfilter", "filtercaps")
    filtercaps.set_property("caps", Gst.Caps.from_string("video/x-raw, format=BGR, width=320, height=240"))
    
    ## element: appsrc
    #src = Gst.ElementFactory.make("appsrc", "src")
    #caps = Gst.caps_from_string("video/x-raw, format=BGR, width=320, height=240, framerate=30/1")
    #src.set_property('caps', caps)
    #src.set_property('blocksize', 320*240*3)
    #src.connect('push-buffer', push_buffer)
    
    ## element: admetadrawer
    drawer = Gst.ElementFactory.make("admetadrawer", "drawer")

    ## element: videoconvert
    videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")

    ## element: appsink
    sink = Gst.ElementFactory.make("appsink", "sink")
    
    # Create the empty pipeline
    pipeline = Gst.Pipeline().new("test-pipeline")
    
    # Build the pipeline
    pipeline_elements = [src, drawer, videoconvert, sink]
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