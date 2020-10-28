from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from hashlib import sha256
import os, os.path
import shutil
import zipfile
import json

# Create your views here.

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), arcname=file)

def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
	if request.method == "POST":
		songs = json.loads(request.body.decode("utf-8"))["songs"]
		hashedIP = sha256(getClientIp(request).encode("utf-8")).hexdigest()
		tmpFolder = os.path.join(settings.TMP_DIR, hashedIP)

		

		response = HttpResponse(content_type='application/zip')

		cmd = f"deemix -p {tmpFolder} {' '.join(songs)}"
		print(cmd)
		os.system(cmd)

		zipf = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED)
		zipdir(tmpFolder, zipf)
		zipf.close()


		#wrapper = FileWrapper(tempZipFile)
		response['Content-Disposition'] = f'attachment; filename=songs.zip'
		
		try:
			shutil.rmtree(tmpFolder)
		except:
			pass

		return response
	else:
		context = {}
		return render(request, "static/downloader/index.html", context)