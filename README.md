This repository contains steps and key notes to develop a serverless video processing application using Lambda, S3 and FFmpeg. <br>
The application consists of :<br>
* S3: To store user video uploads (input) and processed video frames (output).
* Lambda: To automatically process user videos when they are uploaded to S3 using ffmpeg library, without the need for running servers.

## Step 1: Create S3 Buckets
The input and output S3 buckets can be created by running the 'createS3.py' script. </br>

## Step 2: Creating FFmpeg layer
Since ffmpeg library is required to process the video, it needs to be added as a layer.<br>
The steps to create ffmpeg layer are loosely based on [this](https://virkud-sarvesh.medium.com/building-ffmpeg-layer-for-a-lambda-function-a206f36d3edc) medium article and [this](https://aws.amazon.com/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/) aws guide. <br>

### Create FFmpeg zip
Create the ffmpeg zip using the following commands:
```
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5
md5sum -c ffmpeg-release-amd64-static.tar.xz.md5
tar xvf ffmpeg-release-amd64-static.tar.xz
mkdir -p ffmpeg/bin
cp ffmpeg-6.1-amd64-static/ffmpeg ffmpeg/bin/
cd ffmpeg
zip -r ../ffmpeg.zip .
cd ..
ls
```
### Create FFmpeg layer
Create the layer by uploading the zip file from where you downloaded it (S3 or local). <br>
Add the runtime of your lambda function in compatible runtimes. <br>
Finally, add the input S3 bucket as trigger for the function.<br>

### Attach FFmpeg layer
Add the layer in the lambda function whenever you need to use the library.<br>

## Step 3: Create Lambda function
The code for lambda function can be found in 'video-splitting.py'. </br>
Make sure the ffmpeg layer is attached. <br>

### Deployed Application
The lambda function gets triggered when any file is uploaded to the input bucket, processes the files and stores the output in output bucket, all done automatically. <br>


## Step 4: Upload with Workload Generator
Workload Generator simulates a client side and uploads files to the input bucket.</br>

Command to upload:
```
python ./Resources/workload_generator/workload_generator.py --access_key {your access key} --secret_key {your secret key} --input_bucket {input bucket name} --testcase_folder ./Resources/dataset/test_case_1/
```
More information on workload generator can be found in the associated readme.

## Step 5: Test with grading script
The grading script validates the result by matching input and output objects. Furthermore, the script also checks the average execution time for lambda function and the concurrency. <br>
The execution time and concurrency can be controlled by tweaking the memory and ephemeral memory of the lambda function. <br>

Command to test:
```
python grader_script_p1.py --access_key {your access key} --secret_key {your secret key} --input_bucket {input bucket name} --output_bucket input bucket name --lambda_name {lambda function name}
```
The order of testing is:
* Start grading script and run tests 1 and 2.
* Start workload generator script in another terminal.
* Wait for workload generator script to complete execution and then wait again for lambda function to complete execution.
* Finally run test 3-6 of grading script.

More information on grading script can be found in the associated readme.