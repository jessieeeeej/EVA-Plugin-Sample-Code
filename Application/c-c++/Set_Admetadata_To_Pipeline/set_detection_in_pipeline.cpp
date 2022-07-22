// **
// Demo senario: 
// gst-launch-1.0 videotestsrc ! video/x-raw, format=BGR, width=640, height=480, framerate=30/1 ! adsetobjectdetection ! admetadrawer ! videoconvert ! ximagesink

// This example only show how to set adlink metadata.
// So this example does not deal with any other detail concern about snchronize or other tasks.
// Only show how to retrieve the adlink metdata for user who is interested with them.
// **
#include "opencv2/opencv.hpp"
#include <iostream>
#include <stdio.h>
#include <thread>
#include <chrono>
#include <vector>
#include <gst/gst.h>

#include "gstadmeta.h"

using namespace cv;
using namespace std;

static GMainLoop *loop;
GstElement *pipeline, *videotestsrc, *filtercaps, *objectdetection, *drawer, *videoconvert, *appsink, *ximagesink;
vector<Mat> pipeLineOutputVec;
cv::Mat img(cv::Size(640, 480), CV_8UC3);

GstAdBatchMeta* gst_buffer_get_ad_batch_meta(GstBuffer* buffer)
{
    gpointer state = NULL;
    GstMeta* meta;
    const GstMetaInfo* info = GST_AD_BATCH_META_INFO;
    
    while ((meta = gst_buffer_iterate_meta (buffer, &state))) 
    {
        if (meta->info->api == info->api) 
        {
            GstAdMeta *admeta = (GstAdMeta *) meta;
            if (admeta->type == AdBatchMeta)
                return (GstAdBatchMeta*)meta;
        }
    }
    return NULL;
}

static GstFlowReturn new_sample(GstElement *sink, gpointer *udata) 
{
    GstSample *sample;

    g_signal_emit_by_name (sink, "pull-sample", &sample);
    if (sample) 
    {
        GstMapInfo map;
        guint size = 640 * 480 * 3;
        GstBuffer *buffer = gst_buffer_new_allocate (NULL, size, NULL);
        
        buffer = gst_sample_get_buffer (sample);
        
        gst_buffer_map(buffer, &map, GST_MAP_READ);
        
        GstAdBatchMeta *meta = gst_buffer_get_ad_batch_meta(buffer);
        if(meta != NULL)
        {
            AdBatch &batch = meta->batch; 
            VideoFrameData frame_info = batch.frames[0];
            int classificationResultNumber = frame_info.class_results.size();
            cout << "classification result number = " << classificationResultNumber << endl;
            for(int i = 0 ; i < classificationResultNumber ; ++i)
            {
                cout << "========== metadata in application ==========\n";
                cout << "Class = " << frame_info.class_results[i].index << endl;
                cout << "Label = " << frame_info.class_results[i].label << endl;
                cout << "output =  " << frame_info.class_results[i].output << endl;
                cout << "Prob =  " << frame_info.class_results[i].prob << endl;
                cout << "=============================================\n";
            }
        }
        
        memcpy(img.data, (guchar *)map.data, gst_buffer_get_size(buffer));
        pipeLineOutputVec.push_back(img.clone());
        
        gst_buffer_unmap(buffer, &map);
        
        gst_sample_unref (sample);
        this_thread::sleep_for(chrono::milliseconds(1));
        return GST_FLOW_OK;
    }
    
    return GST_FLOW_ERROR;
}



static void free_pipeline()
{
    gst_element_set_state (pipeline, GST_STATE_NULL);
    gst_object_unref (GST_OBJECT (pipeline));
    g_main_loop_unref (loop);
}
static void establish_thread_pipeline()
{
    /* init GStreamer */
    gst_init (NULL, NULL);
    loop = g_main_loop_new (NULL, FALSE);

    /* setup pipeline */
    pipeline = gst_pipeline_new ("pipeline");
    videotestsrc = gst_element_factory_make ("videotestsrc", "source");
    filtercaps = gst_element_factory_make ("capsfilter", "filtercaps");
    objectdetection = gst_element_factory_make ("adsetobjectdetection", "objectdetection");
    drawer = gst_element_factory_make("admetadrawer", "drawer");
    videoconvert = gst_element_factory_make("videoconvert", "videoconvert");
    ximagesink = gst_element_factory_make("ximagesink", "ximagesink");

    /* setup filtercaps*/
    g_object_set (G_OBJECT (filtercaps), "caps",
                  gst_caps_new_simple ("video/x-raw", "format", G_TYPE_STRING, "BGR",
                                       "width", G_TYPE_INT, 640, "height", G_TYPE_INT, 480,
                                       "framerate", GST_TYPE_FRACTION, 30, 1, NULL), NULL);
    gst_bin_add_many (GST_BIN (pipeline), videotestsrc, filtercaps, objectdetection, drawer, videoconvert, ximagesink, NULL);
    gst_element_link_many (videotestsrc, filtercaps, objectdetection, drawer, videoconvert, ximagesink, NULL);
    
    /* play */
    gst_element_set_state (pipeline, GST_STATE_PLAYING);
    g_main_loop_run (loop);
    
    free_pipeline();
}


int main(int, char**)
{
    thread pipethread(establish_thread_pipeline);
    cv::Mat img_show(cv::Size(640, 480), CV_8UC3);
    while(true)
    {
        if(pipeLineOutputVec.size() > 0)
        {
            img_show = pipeLineOutputVec[0].clone();
            imwrite("a.bmp", img_show);
            pipeLineOutputVec.erase(pipeLineOutputVec.begin());
        }
        this_thread::sleep_for(chrono::milliseconds(1));
    }
    
    return 0;
}
