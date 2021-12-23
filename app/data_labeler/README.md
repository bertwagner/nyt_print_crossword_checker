# Data Labeler

This small Flask app helps labeling data.  

It assumes all files are uniquely named and checks to see which files in the input directory are not present anywhere in the output directory.  

It then displays those not-yet-labeled images with the default best guess of what that image should be labeled as.  Any labels can be edited if they are not correct.

Once the Save button is pressed, it copies all of the not-yet-processed images to the correct labeled location in the output directory.