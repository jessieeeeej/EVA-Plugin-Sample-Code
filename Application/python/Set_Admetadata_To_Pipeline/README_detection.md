# Object detection
## What can you learn from this sample code?
Through this sample code, you can learn:

1. Establish a basic gstreamer pipeline in an application program.
2. Set detection results from admetadata.
3. Set stream data by using plugin **detection_sample** in application program.

## Essential knowledge
1. Understand plugin sample codes: **detection_sample.py**.
2. ADLINK metadata structure. The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5.
3. Basic Python programming.

## About this sample code
This sample shows you how to set the adlink metadata by using plugin. The target created pipeline command is:

    gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! detection_sample ! admetadrawer ! videoconvert ! ximagesink

The detection_sample is the plugin that generated a random inferenced detection results to metadata.

## Description
This sample shows you how to set the adlink metadata by using plugin. First, import the gst_admeta.py:

    # Required to import to get ADLINK inference metadata
    import gst_admeta as admeta
    
Second, add plugin **detection_sample** to the pipeline. This element will generate random detection result of each frame:

    if __name__ == '__main__':
        print('Start establish pipeline.')
        # Initialize GStreamer
        Gst.init(sys.argv)

        # Create the elements
        
        # ... code omitted
        
        ## element: detection_sample
        detection = Gst.ElementFactory.make("detection_sample", "detection")

        # ... code omitted

        # Build the pipeline
        pipeline_elements = [videosrc, filtercaps, detection, drawer, videoconvert, sink]
        establish_pipeline(pipeline, pipeline_elements)
    
The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5. Or can be found in the file:

    EVA_INSTALL_ROOT/plugins/python/gst_admeta.py
    
Based on the structure, the frame in vector and the inferenced data are stored in each frame need to be set up. When data in this element is empty, we’ll randomly generate the inference data and set data into the detection result. The simulated result will be set into adbatchmetadata with frame information.

## Run this sample code
First, copy the built plugin **libadsetobjectdetection.so** file to the plugin folder EVA installed, here used EVA_ROOT to preset the installed path of EVASDK. Then, go to the folder of the binary and run binary in terminal or cmd:

    $ python3 set_detection_in_pipeline.py 

and you will see the inference result displayed frame by frame in the window:

    (video)
