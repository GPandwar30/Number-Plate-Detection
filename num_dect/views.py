# detection/views.py
import cv2
import numpy as np
import os
import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ImageUploadForm
from django.http import StreamingHttpResponse
from .models import ImageUpload


harcascate = os.path.join(settings.BASE_DIR, 'haarcascade_russian_plate_number.xml')
min_area = 500
output_folder = 'scanned_plates'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def detect_plate_image(image):
    plate_cascade = cv2.CascadeClassifier(harcascate)
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in plates:
        area = w * h
        if area > min_area:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, "Number plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            files_in_output_folder = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder,name))])
            count = files_in_output_folder
            
            cropped_plate = image[y:y + h, x:x + w]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f'{output_folder}/detected_plate_{count}_{timestamp}.jpg'
            cv2.imwrite(filename, cropped_plate)

            # Save to the database
            scanned_image = ImageUpload(image=f'scanned_plates/detected_plate_{count}_{timestamp}.jpg')
            scanned_image.save()

    return image

# View to handle file uploads
def upload_image_view(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            image_path = os.path.join(settings.MEDIA_ROOT, str(image_instance.image))
            image = cv2.imread(image_path)
            result_image = detect_plate_image(image)

            result_image_path = os.path.join(settings.MEDIA_ROOT, 'result.jpg')
            cv2.imwrite(result_image_path, result_image)

            return render(request, 'result.html', {'result_image': 'result.jpg'})
    else:
        form = ImageUploadForm()
    
    return render(request, 'upload_image.html', {'form': form})

# View to stream live detection using the camera
def live_stream_view(request):
    return render(request, 'live_stream.html')

def video_feed():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = detect_plate_image(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

def video_stream(request):
    return StreamingHttpResponse(video_feed(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')