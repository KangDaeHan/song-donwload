import os
from django.http import FileResponse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import youtube_dl

class YouTubeAudioDownloadView(APIView):
    def get(self, request, video_url):
        # Validate the video URL
        validate = URLValidator()
        try:
            validate(video_url)
        except ValidationError:
            return Response({'error': 'Invalid YouTube video URL'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Set up youtube-dl options for audio download
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': 'media/%(title)s.%(ext)s',  # Output file location
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)

            # Check if the audio file was downloaded successfully
            if 'entries' in info_dict:
                audio_file_path = os.path.join('media', f"{info_dict['entries'][0]['title']}.mp3")
                return FileResponse(open(audio_file_path, 'rb'))

            raise Http404('Audio file not found')

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)