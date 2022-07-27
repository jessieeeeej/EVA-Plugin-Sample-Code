// **
// Demo senario: 
// gst-launch-1.0 videotestsrc ! video/x-raw, format=BGR, width=640, height=480, framerate=30/1 ! adsetclassification ! admetadrawer ! videoconvert ! ximagesink

// This example only show how to get adlink metadata from appsink.
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
GstElement *pipeline, *videotestsrc, *filtercaps, *classifier, *drawer, *videoconvert, *appsink, *ximagesink;
vector<Mat> pipeLineOutputVec;
cv::Mat img(cv::Size(640, 480), CV_8UC3);

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
    classifier = gst_element_factory_make ("adsetclassification", "classifier");
    drawer = gst_element_factory_make("admetadrawer", "drawer");
    videoconvert = gst_element_factory_make("videoconvert", "videoconvert");
    //appsink = gst_element_factory_make ("appsink", "appsink");
    ximagesink = gst_element_factory_make("ximagesink", "ximagesink");

    /* setup filtercaps*/
    g_object_set (G_OBJECT (filtercaps), "caps",
                  gst_caps_new_simple ("video/x-raw", "format", G_TYPE_STRING, "BGR",
                                       "width", G_TYPE_INT, 640, "height", G_TYPE_INT, 480,
                                       "framerate", GST_TYPE_FRACTION, 30, 1, NULL), NULL);
    gst_bin_add_many (GST_BIN (pipeline), videotestsrc, filtercaps, classifier, drawer, videoconvert, ximagesink, NULL);
    gst_element_link_many (videotestsrc, filtercaps, classifier, drawer, videoconvert, ximagesink, NULL);
    
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
