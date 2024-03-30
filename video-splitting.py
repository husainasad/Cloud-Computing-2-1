import os
import boto3
import json
import subprocess
import math

FFMPEG_PATH = '/opt/bin/ffmpeg'
TEMP_DIR = '/tmp'

with open('lambda_config.json') as f:
    config = json.load(f)

region = config.get("AWS_REGION") 
input_bucket = config.get("INPUT_BUCKET")
output_bucket = config.get("STAGE1_BUCKET")
timeout = config.get("URL_TIMEOUT")

session = boto3.Session(region_name=region)
s3_client = session.client('s3')
    
def video_duration(video_url):
    duration_cmd = f'{FFMPEG_PATH} -i "{video_url}" -f null -'
    
    try:
        output = subprocess.check_output(duration_cmd, stderr=subprocess.STDOUT, shell=True)
        duration_str = str(output).split("Duration: ")[1].split(",")[0]
        duration_list = duration_str.split(":")
        duration_seconds = int(duration_list[0]) * 3600 + int(duration_list[1]) * 60 + float(duration_list[2])
        return duration_seconds
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None
        
def video_splitting_cmdline(video_url, video_filename):
    outdir = os.path.join(TEMP_DIR, os.path.splitext(os.path.basename(video_filename))[0])
    os.makedirs(outdir, exist_ok=True)
    
    # original cmd
    # split_cmd = f'{FFMPEG_PATH} -ss 0 -r 1 -i "{video_url}" -vf fps=1/10 -start_number 0 -vframes 10 "{outdir}/output-%02d.jpg" -y'

    # Unevenly spaced frames
    # split_cmd = f'{FFMPEG_PATH} -ss 0 -r 1 -i "{video_url}" -vf fps=1 -start_number 0 -vframes 10 "{outdir}/output-%02d.jpg" -y'
    
    # Evenly spaced frames

    # Get video duration using ffmpeg
    video_duration_sec = video_duration(video_url)

    if video_duration_sec is None:
        print("Error: Failed to get video duration.")
        return None
    
    total_frames = 10
    frame_interval = max(math.ceil(video_duration_sec / total_frames), 1)

    split_cmd = f'{FFMPEG_PATH} -i "{video_url}" -vf "select=not(mod(n\,{frame_interval}))" -fps_mode vfr -q:v 2 -start_number 0 -vframes {total_frames} "{outdir}/output-%02d.jpg" -y'
    
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

    # Not required
    # fps_cmd = f'{FFMPEG_PATH} -i "{video_url}" 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    # fps = subprocess.check_output(fps_cmd, shell=True).decode("utf-8").rstrip("\n")
    # fps = math.ceil(float(fps))
    
    return outdir
    
def generate_presigned_url(key):
    try:
        url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': input_bucket, 'Key': key}, ExpiresIn=timeout)
        return url
    except Exception as e:
        print(f"Error generating presigned url : {str(e)}")

def upload_frames_to_s3(output_dir, video_key):
    try:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                s3_key = f"{os.path.splitext(video_key)[0]}/{file}"
                s3_client.put_object(Bucket=output_bucket, Key=s3_key, Body=open(file_path, 'rb'))
                print(f"Uploaded {file_path} to s3://{output_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error uploading frames to S3: {str(e)}")
        
def process_video(video_key):
    try:
        video_url = generate_presigned_url(video_key)
        output_dir = video_splitting_cmdline(video_url, video_key)
        print(f"Video '{video_key}' processed successfully")

        if output_dir:
            upload_frames_to_s3(output_dir, video_key)
    except Exception as e:
        print(f"Error processing video '{video_key}': {str(e)}")

def process_objects():
    try:
        response = s3_client.list_objects_v2(Bucket=input_bucket)
        for obj in response.get('Contents', []):
            video_key = obj['Key']
            process_video(video_key)
    except Exception as e:
        print("Unable to get bucket objects")

def lambda_handler(event, context):
    try:
        # process_objects()
        video_key = event['Records'][0]['s3']['object']['key']
        process_video(video_key)
        return {
            'statusCode': 200,
            'body': 'Function executed successfully'
        }
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Error processing video'
        }