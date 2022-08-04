# Object-detection
## What can you learn from this sample code?
Through this sample code, you can learn:

1. Establish a basic gstreamer pipeline in an application program.
2. Set object-detection results to admetadata.
3. Set stream data by using element appsrc in application program.

## Essential knowledge
1. Understand plugin sample codes: "Get stream data from pipeline".
2. ADLINK metadata structure. The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5.
3. Basic C/C++ programming.

## About this sample code
This sample code creates two command pipelines in an application.

•	First pipeline created for capturing from videosrc through OpenCV VideoCapture:

    videotestsrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! appsink
    
•	Second pipeline created in thread:

    appsrc ! admetadrawer ! videoconvert ! ximagesink
    
VideoCapture reads frame from the video and push them into buffer, grabBuffer. The appsrc will notice callback function, need_data, to feed image data and set object-detection, then continuously processing downstream in the pipeline. Each processed image will be displayed with random object-detection label in the video.

## Description
OpenCV provides a convenient way for developers wanting to utilize their own API, algorithm, or unique processing. The pipeline in thread provides user to request frame data. This sample shows you how to set the adlink metadata to the buffer. 

First, include the gstadmeta.h:

    #include "gstadmeta.h"
    
Second, build the pipeline in thread:

    appsrc ! admetadrawer ! videoconvert ! ximagesink

shown in the code fragment below:

    static void establish_thread_pipeline()
    {
        /* init GStreamer */
        gst_init (NULL, NULL);
        loop = g_main_loop_new (NULL, FALSE);

        /* setup pipeline */
        pipeline = gst_pipeline_new ("pipeline");
        appsrc = gst_element_factory_make ("appsrc", "appsrc");
        drawer = gst_element_factory_make("admetadrawer", "drawer");
        videoconvert = gst_element_factory_make("videoconvert", "videoconvert");
        ximagesink = gst_element_factory_make("ximagesink", "ximagesink");

        /* setup appsrc*/
        g_object_set (G_OBJECT (appsrc), "caps",
        gst_caps_new_simple ("video/x-raw", "format", G_TYPE_STRING, "BGR",
                                            "width", G_TYPE_INT, 640, "height", G_TYPE_INT, 480,
                                            "framerate", GST_TYPE_FRACTION, 30, 1,NULL), NULL);

        gst_bin_add_many (GST_BIN (pipeline), appsrc, drawer, videoconvert, ximagesink, NULL);
        gst_element_link_many (appsrc, drawer, videoconvert, ximagesink, NULL);

        g_object_set (G_OBJECT (appsrc), "stream-type", 0, "format", GST_FORMAT_TIME, NULL);
        g_signal_connect (appsrc, "need-data", G_CALLBACK (cb_need_data), NULL);

        /* play */
        gst_element_set_state (pipeline, GST_STATE_PLAYING);

        while(true)
        {
            this_thread::sleep_for(chrono::milliseconds(10));
        }
        free_pipeline();
    }
        
Refer to the GStreamer tutorials for more information on how to build the pipeline or our sample "Generate a basic pipeline".
After setting the appsrc property "cap", "blocksize" to the format we are going to push, connect the cb_need_data callback function to need-data to wait for the appsrc notification to feed the data and then push it to appsrc or end the data. The code blocks below shows how to set the object-detection metadata by cb_need_data function:

    static void cb_need_data(GstElement *appsrc, guint unused_size, gpointer user_data)
    {
        static GstClockTime timestamp = 0;
        gpointer state = NULL;
        GstBuffer *buffer;
        GstAdBatchMeta* meta;
        const GstMetaInfo* info = GST_AD_BATCH_META_INFO;
        guint size;
        GstFlowReturn ret;
        GstMapInfo map;

        size = cols * rows * channels;

        buffer = gst_buffer_new_allocate (NULL, size, NULL);
        gst_buffer_map(buffer, &map, GST_MAP_WRITE);

        if( grabVec.size() > 0 )
        {
            memcpy((guchar *)map.data, grabVec[0].data, gst_buffer_get_size(buffer));
            grabVec.erase(grabVec.begin());
        }
        gst_buffer_unmap(buffer, &map);

        GST_BUFFER_PTS (buffer) = timestamp;
        GST_BUFFER_DURATION (buffer) = gst_util_uint64_scale_int (1, GST_SECOND, 2);

        timestamp += GST_BUFFER_DURATION (buffer);

        meta = (GstAdBatchMeta *)gst_buffer_add_meta(buffer, info, &state);

        bool frame_exist = meta->batch.frames.size() > 0 ? true : false;
        if(!frame_exist)
        {
            VideoFrameData frame_info;
            std::vector<std::string> labels = {"water bottle", "camera", "chair", "person", "slipper"};
            std::vector<adlink::ai::DetectionBoxResult> random_boxes;
            srand( time(NULL) );
            
            // Generate random dummy boxes here
            adlink::ai::DetectionBoxResult random_box;
            int i = rand() % 5;
            random_box.obj_id = i;
            random_box.obj_label = labels[i];
            random_box.prob = (double)( rand() % 1000 )/1000;
            random_box.x1 = (double)( rand() % 3 + 1 )/10;	// 0.1~0.3
            random_box.x2 = (double)( rand() % 3 + 7 )/10;	// 0.7~0.9
            random_box.y1 = (double)( rand() % 3 + 1 )/10;	// 0.1~0.3
            random_box.y2 = (double)( rand() % 3 + 7 )/10;	// 0.7~0.9
            
            frame_info.stream_id = " ";
            frame_info.width = cols;
            frame_info.height = rows;
            frame_info.depth = depth;
            frame_info.channels = channels;
            frame_info.device_idx = 0;
            frame_info.detection_results.push_back(random_box);
            meta->batch.frames.push_back(frame_info);
        }

        g_signal_emit_by_name (appsrc, "push-buffer", buffer, &ret);
        gst_buffer_unref (buffer);

        if (ret != GST_FLOW_OK) 
            g_main_loop_quit (loop);
    }
    
Once the function is called back, the data for appsrc's buffer can be padded and then the signal called to push the data to appsrc.
The metadata structure could be find in Edge Vision Analytics SDK Programming Guide : How to Use ADLINK Metadata in Chapter 5. Or can be found in the file:

• EVA_INSTALL_ROOT/include/gstadmeta.h

• EVA_INSTALL_ROOT/include/libs/ai/structure.h

Based on the structure, AdBatchMeta can set the frame and the inferenced data which stored in each frame based on classification, detection, segmentation or openpose. When the meta data of the buffer is empty, we’ll randomly generate inference data and set data into the classification result. The simulated result will be set into adbatchmetadata with frame information.

## Run this sample code
Go to the folder of the binary and run in terminal or cmd:

    ./set_detection_in_pipeline

and you will see the inference result displayed frame by frame in the window:

    (video)
