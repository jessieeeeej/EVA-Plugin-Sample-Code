## What can you learn from this sample code?

Through this sample code, you can learn:
1.	Set detection results into admetadata.

## Essential knowledge

1.	Plugin sample code, "video filtr", in C/C++.
2.	The difference between application code and plugin/element code.
3.	ADLINK metadata structure. The metadata structure could be find in Edge Vision Analytics SDK Programming Guide: How to Use ADLINK Metadata in Chapter 5.
4.	Basic C/C++ programming.

## About this sample code

This sample shows how to set the adlink metadata inside the element. The target created pipeline command is:

    $ gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! adsetobjectdetection ! admetadrawer ! videoconvert ! ximagesink
  
This command is used to display the simulated inferenced object detection result and the element(this sample code), adsetobjectdetection, set the simulated detection data into admetadata.

## Description

This sample shows how to set the adlink metadata inside the element. First, include the gstadmeta.h:

    #include "gstadmeta.h"
  
Second, in the virtual method, ad_set_object_detection_transform_frame_ip, of this sample has an extra code block, setObjectDetectionData, which is going to set the detection metadata:

    gpointer state = NULL;
    GstAdBatchMeta* meta;
    const GstMetaInfo* info = GST_AD_BATCH_META_INFO;
    meta = (GstAdBatchMeta *)gst_buffer_add_meta(buffer, info, &state);

    bool frame_exist = meta->batch.frames.size() > 0 ? true : false;
    if(!frame_exist)
    {
        VideoFrameData frame_info;
        std::vector<adlink::ai::DetectionBoxResult> arr;
        std::vector<std::string> labels = {"water bottle", "camera", "chair", "person", "slipper"};
        std::vector<adlink::ai::DetectionBoxResult> random_boxes;
        srand( time(NULL) );

        // Generate 5 random dummy boxes here
        for ( int i = 0 ; i < 5 ; i++ )
        {
            adlink::ai::DetectionBoxResult temp_box;
            temp_box.obj_id = i+1;
            temp_box.obj_label = labels[i];
            temp_box.prob = (double)( rand() % 1000 )/1000;
            temp_box.x1 = (double)( rand() % 3 + 1 )/10;	// 0.1~0.3
            temp_box.x2 = (double)( rand() % 3 + 7 )/10;	// 0.7~0.9
            temp_box.y1 = (double)( rand() % 3 + 1 )/10;	// 0.1~0.3
            temp_box.y2 = (double)( rand() % 3 + 7 )/10;	// 0.7~0.9
            random_boxes.push_back(temp_box);
        }

        frame_info.stream_id = " ";
        frame_info.width = 640;
        frame_info.height = 480;
        frame_info.depth = 0;
        frame_info.channels = 3;
        frame_info.device_idx = 0;
        frame_info.detection_results.push_back(random_boxes[rand()%5]);
        meta->batch.frames.push_back(frame_info);
    }
    
The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5. Or can be found in the files:

•	EVA_INSTALL_ROOT/include/gstadmeta.h

•	EVA_INSTALL_ROOT/include/libs/ai/structure.h
Based on the structure, AdBatchMeta can set the frame and the inferenced data which stored in each frame based on classification, detection, segmentation or openpose. When the meta data of the buffer is empty, we’ll randomly generate the inference data and set data into the detection result. The simulated result will be set into adbatchmetadata with frame information.

## Run this sample code

Copy the built plugin libadsetobjectdetection.so file to the plugin folder EVA installed, here used EVA_ROOT to preset the installed path of EVASDK. Then run the pipeline command for testing:

    $ gst-launch-1.0 videotestsrc ! video/x-raw, width=640, height=480 ! adsetobjectdetection ! admetadrawer ! videoconvert ! ximagesink
and you will see the inference result displayed frame by frame in the window:

    (video)
