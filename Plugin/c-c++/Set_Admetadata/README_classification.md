## What can you learn from this sample code?

Through this sample code, you can learn:
1.	Set classification results into admetadata.
Essential knowledge
1.	Plugin sample code, "video filtr", in C/C++.
2.	The difference between application code and plugin/element code.
3.	ADLINK metadata structure. The metadata structure could be find in Edge Vision Analytics SDK Programming Guide: How to Use ADLINK Metadata in Chapter 5.
4.	Basic C/C++ programming.

## About this sample code

This sample shows how to set the adlink metadata inside the element. The target created pipeline command is:

    $ gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! adsetclassification ! admetadrawer ! videoconvert ! ximagesink
    
This command is used to display the simulated inferenced classification result and the element(this sample code), adsetclassification, set the simulated classification data into admetadata.

## Description

This sample shows how to set the adlink metadata inside the element. First, include the gstadmeta.h:

    #include "gstadmeta.h"
    
Second, in the virtual method, ad_set_classification_transform_frame_ip, of this sample has an extra code block, setClassificationData, which is going to set the classification metadata:

    gpointer state = NULL;
    GstAdBatchMeta* meta;
    const GstMetaInfo* info = GST_AD_BATCH_META_INFO;
    meta = (GstAdBatchMeta *)gst_buffer_add_meta(buffer, info, &state);
        
    bool frame_exist = meta->batch.frames.size() > 0 ? true : false;
    if(!frame_exist)
    {
        VideoFrameData frame_info;
	    std::vector<std::string> labels = {"water bottle", "camera", "chair", "person", "slipper", "mouse", "Triceratops", "woodpecker"};
	    srand( time(NULL) );
		
	    // Create random labels
	    adlink::ai::ClassificationResult classification;
	    classification.index = (rand() % labels.size());
	    classification.output = "";
	    classification.label = labels[classification.index];
	    classification.prob = (double)classification.index / labels.size();

        frame_info.stream_id = " ";
	    frame_info.width = 640;
        frame_info.height = 480;
        frame_info.depth = 0;
        frame_info.channels = 3;
        frame_info.device_idx = 0;
        frame_info.class_results.push_back(classification);
	    meta->batch.frames.push_back(frame_info);
    }

The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5. Or can be found in the files:
•	EVA_INSTALL_ROOT/include/gstadmeta.h
•	EVA_INSTALL_ROOT/include/libs/ai/structure.h

Based on the structure, the frame in vector and the inferenced data are stored in each frame need to be set up. When data in this element is empty, we’ll randomly generate the inference data and set data into the classification result. The simulated result will be set into adbatchmetadata with frame information.

## Run this sample code

Copy the built plugin libadsetclassification.so file to the plugin folder EVA installed, here used EVA_ROOT to preset the installed path of EVASDK. Then run the pipeline command for testing:

    $ gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! adsetclassification ! admetadrawer ! videoconvert ! ximagesink
and you will see the inference result displayed frame by frame in the window:

    (video)

