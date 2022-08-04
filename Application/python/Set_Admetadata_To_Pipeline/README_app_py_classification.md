# Classification
## What can you learn from this sample code?
Through this sample code, you can learn:

1. Establish a basic gstreamer pipeline in an application program.
2. Set classification results to admetadata.
3. Set stream data by using element appsrc in application program.

## Essential knowledge
1. Understand plugin sample codes: "Get stream data from pipeline".
2. ADLINK metadata structure. The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5.
3. Basic Python programming.

## About this sample code
This sample code creates two command pipelines in an application.

•	First pipeline created for capturing from videosrc through OpenCV VideoCapture:

    videotestsrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! appsink
    
•	Second pipeline created in thread:

    appsrc ! admetadrawer ! videoconvert ! ximagesink
    
VideoCapture reads frame from the video and push them into buffer, grabBuffer. The appsrc will notice callback function, need_data, to feed image data and set classification, then continuously processing downstream in the pipeline. Each processed image will be displayed with random classification label in the video.

## Description
OpenCV provides a convenient way for developers wanting to utilize their own API, algorithm, or unique processing. The pipeline in thread provides user to request frame data. This sample shows you how to set the adlink metadata to the buffer. 

First, import the gst_admeta.py:

    import gst_admeta as admeta
    
Second, build the pipeline in thread:

    appsrc ! admetadrawer ! videoconvert ! ximagesink

shown in the code fragment below:

    def establish_thread_pipeline():
        print('Start establish thread pipeline.')
        # Initialize GStreamer
        Gst.init(sys.argv)

        # Create the elements
        ## element: appsrc
        src = Gst.ElementFactory.make("appsrc", "src")
        caps = Gst.caps_from_string("video/x-raw,format=BGR,width=640,height=480,framerate=30/1")
        src.set_property('caps', caps)
        src.set_property('blocksize', 640*480*3)
        src.set_property('emit-signals', True)
        src.connect('need-data', need_data)
        src.connect('enough-data', enough_data)
        ## element: admetadrawer
        drawer = Gst.ElementFactory.make("admetadrawer", "drawer")
        ## element: videoconvert
        videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
        ## element: ximagesink
        sink = Gst.ElementFactory.make("ximagesink", "sink")
        # Create the empty pipeline
        pipeline = Gst.Pipeline().new("test-pipeline")
        # Build the pipeline
        pipeline_elements = [src, drawer, videoconvert, sink]
        
        establish_pipeline(pipeline, pipeline_elements)
        
        # Start pipeline
        pipeline.set_state(Gst.State.PLAYING)
        loop = GLib.MainLoop()
        # Wait until error or EOS
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", on_message, loop)

        try:
            print("Start to run the pipeline in thread.\n")
            loop.run()
        except Exception:
            traceback.print_exc()
            loop.quit()

        # Stop Pipeline
        pipeline.set_state(Gst.State.NULL)
        del pipeline
        print('pipeline stopped.\n')
        
Refer to the GStreamer tutorials for more information on how to build the pipeline or our sample "Generate a basic pipeline".
After setting the appsrc property "cap", "blocksize" to the format we are going to push, connect the need_data and enough_data callback function to need-data and enough-data to wait for the appsrc notification to feed the data and then push it to appsrc or end the data. The code blocks below shows how to set the classification metadata by need_data function:

    def need_data(src, length) -> Gst.FlowReturn:
        # wait for image data vector, grabBuffer, is not full
        while True:
            time.sleep(0.001)
            if grabBuffer.qsize() > 0:
                break

        global num_frames
        if grabBuffer.qsize() > 0:
            # get image data from vector
            buf = Gst.Buffer.new_allocate(None, length, None)
            buf.fill(0, grabBuffer.get().tostring())

            # set buffer timestamp
            buf.duration = 1/ 30 * Gst.SECOND
            buf.pts = buf.dts = int(num_frames * buf.duration)
            buf.offset = num_frames * buf.duration
            num_frames += 1

            # create random classification
            cls = []
            labels = ['water bottle', 'camera', 'chair', 'person', 'slipper', 'mouse', 'Triceratops', 'woodpecker']
            class_id = random.randrange(len(labels))
            class_prob = random.uniform(0, 1)
            cls.append(admeta._Classification(class_id, '', labels[class_id], class_prob))

            # set classification into buffer
            pad_list = src.get_pad_template_list()
            pad = Gst.Element.get_static_pad(src, pad_list[0].name_template)
            admeta.set_classification(buf, pad, cls)

            # push buffer to appsrc
            retval = src.emit('push-buffer', buf)

            if retval != Gst.FlowReturn.OK:
                print("retval = ", retval)

            time.sleep(0.01)

    def enough_data(src, size, length) -> Gst.FlowReturn:
        return Gst.FlowReturn.OK
    
Once the function is called back, the data for appsrc's buffer can be padded and then the signal called to push the data to appsrc.
The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5. Or can be found in the file:

•	EVA_INSTALL_ROOT/plugins/python/gst_admeta.py
    
Based on the structure, AdBatchMeta can set the frame and the inferenced data which stored in each frame based on classification, detection, segmentation or openpose. When the meta data of the buffer is empty, we’ll randomly generate the inference data and set data into the classification result. The simulated result will be set into adbatchmetadata with frame information.

## Run this sample code
Go to the folder of the python code and run in terminal or cmd:

    $ python3 set_classification_in_pipeline.py 

and you will see the inference result displayed frame by frame in the window:

    (video)
